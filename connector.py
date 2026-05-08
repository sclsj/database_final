"""Load scraped 3ie records from JSON into the normalized MySQL schema.

This script rebuilds the project schema from ``schema.sql`` and then imports
``data_output.json`` into the relational tables used by the project. The
source JSON contains placeholder text and a few inconsistent field shapes, so
the loader normalizes text and uses defensive iteration where needed.
"""

import json
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request

import mysql.connector


PLACEHOLDER_VALUES = {
    "not specified",
    "not reported",
    "not applicable",
    "not applicable (no studies)",
    "na",
    "n/a",
    "unspecified",
    "none",
    "not available",
}

WIKIDATA_USER_AGENT = "3ie-final-project/1.0 (agency country lookup)"
WIKIDATA_MIN_INTERVAL_SECONDS = 0.2
WIKIDATA_RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
WIKIDATA_SEARCH_CACHE = {}
WIKIDATA_ENTITY_CACHE = {}
WIKIDATA_LAST_REQUEST_AT = 0.0
WIKIDATA_ENTITY_COUNTRY_PROPERTIES = ("P17", "P495")
WIKIDATA_LOCATION_PROPERTIES = ("P159", "P740", "P276", "P131")

AGENCY_NON_VALUES = {
    "999",
    "no external funding",
    "no funding received",
    "no funding recieved",
    "no funding was received for this research",
    "not applicabl",
    "not mentioned",
    "other",
}

COUNTRY_ALIAS_MAP = {
    "american": "United States",
    "argentina": "Argentina",
    "argentinean": "Argentina",
    "australia": "Australia",
    "australian": "Australia",
    "belgian": "Belgium",
    "belgium": "Belgium",
    "brazil": "Brazil",
    "british": "United Kingdom",
    "canada": "Canada",
    "canadian": "Canada",
    "chile": "Chile",
    "china": "China",
    "colombia": "Colombia",
    "danish": "Denmark",
    "denmark": "Denmark",
    "england": "United Kingdom",
    "ethiopia": "Ethiopia",
    "finland": "Finland",
    "finnish": "Finland",
    "france": "France",
    "french": "France",
    "german": "Germany",
    "germany": "Germany",
    "ghana": "Ghana",
    "hong kong": "Hong Kong",
    "india": "India",
    "indian": "India",
    "indonesia": "Indonesia",
    "indonesian": "Indonesia",
    "ireland": "Ireland",
    "irish": "Ireland",
    "italy": "Italy",
    "japan": "Japan",
    "japanese": "Japan",
    "kenya": "Kenya",
    "lebanese": "Lebanon",
    "lebanon": "Lebanon",
    "malawi": "Malawi",
    "malaysia": "Malaysia",
    "malaysian": "Malaysia",
    "morocco": "Morocco",
    "netherlands": "Netherlands",
    "new zealand": "New Zealand",
    "norway": "Norway",
    "norwegian": "Norway",
    "pakistan": "Pakistan",
    "portugal": "Portugal",
    "portuguese": "Portugal",
    "scotland": "United Kingdom",
    "south africa": "South Africa",
    "spain": "Spain",
    "sri lanka": "Sri Lanka",
    "sweden": "Sweden",
    "swedish": "Sweden",
    "swiss": "Switzerland",
    "switzerland": "Switzerland",
    "taiwan": "Taiwan",
    "thailand": "Thailand",
    "uk": "United Kingdom",
    "united kingdom": "United Kingdom",
    "united states": "United States",
    "usa": "United States",
    "wales": "United Kingdom",
}

AGENCY_COUNTRY_OVERRIDES = {
    "bill and melinda gates foundation": "United States",
    "center for international forestry research cifor": "Indonesia",
    "centers for disease control and prevention cdc": "United States",
    "childrens investment fund foundation ciff": "United Kingdom",
    "deutsche forschungsgemeinschaft dfg": "Germany",
    "economic and social research council esrc": "United Kingdom",
    "european commission": "Belgium",
    "european union eu": "Belgium",
    "global alliance for improved nutrition gain": "Switzerland",
    "international development and research centre idrc": "Canada",
    "international initiative for impact evaluation 3ie": "India",
    "joint united nations programme on hiv aids unaids": "Switzerland",
    "medical research council mrc uk": "United Kingdom",
    "national institute for health research nihr": "United Kingdom",
    "national institutes of health nih usa": "United States",
    "norwegian agency for development cooperation norad": "Norway",
    "swedish international development agency sida": "Sweden",
    "uk govt dfid fcdo": "United Kingdom",
    "united nations childrens fund unicef": "United States",
    "wellcome trust": "United Kingdom",
    "world bank group": "United States",
    "world food programme wfp": "Italy",
    "world health organization who": "Switzerland",
}

ORGANIZATION_HINTS = (
    "academy",
    "agency",
    "aid",
    "alliance",
    "association",
    "authority",
    "bank",
    "board",
    "center",
    "centre",
    "college",
    "commission",
    "committee",
    "consortium",
    "council",
    "corporation",
    "department",
    "foundation",
    "fund",
    "government",
    "group",
    "hospital",
    "institute",
    "institution",
    "laboratories",
    "laboratory",
    "ministry",
    "office",
    "organisation",
    "organization",
    "philanthropies",
    "school",
    "service",
    "society",
    "trust",
    "university",
)

NON_AGENCY_HINTS = (
    "project",
    "programme",
    "program",
    "study",
    "trial",
    "topic",
    "plan",
    "survey",
)



def clean_text(value):
    """Collapse whitespace and convert empty values to ``None``."""
    if value is None:
        return None

    cleaned = " ".join(str(value).split())
    return cleaned or None


def clean_and_remove_placeholder(value):
    """Normalize text and treat known placeholder strings as missing data."""
    cleaned = clean_text(value)
    if cleaned is None:
        return None
    if cleaned.lower() in PLACEHOLDER_VALUES:
        return None
    return cleaned


def normalize_lookup_text(value):
    """Reduce agency text to a comparable ASCII token form."""
    cleaned = clean_text(value)
    if cleaned is None:
        return None

    normalized = unicodedata.normalize("NFKD", cleaned)
    normalized = normalized.encode("ascii", "ignore").decode("ascii")
    normalized = normalized.lower().replace("&", " and ")
    normalized = re.sub(r"[’'`´]", "", normalized)
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    normalized = " ".join(normalized.split())
    return normalized or None


def throttle_wikidata_requests():
    """Keep API calls slow enough to avoid Wikidata rate limits."""
    global WIKIDATA_LAST_REQUEST_AT

    elapsed = time.time() - WIKIDATA_LAST_REQUEST_AT
    if elapsed < WIKIDATA_MIN_INTERVAL_SECONDS:
        time.sleep(WIKIDATA_MIN_INTERVAL_SECONDS - elapsed)
    WIKIDATA_LAST_REQUEST_AT = time.time()


def fetch_wikidata_json(url, max_attempts=4):
    """Fetch JSON from Wikidata with a user agent and simple retries."""
    for attempt in range(max_attempts):
        throttle_wikidata_requests()
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": WIKIDATA_USER_AGENT,
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            if exc.code not in WIKIDATA_RETRY_STATUS_CODES or attempt == max_attempts - 1:
                return None
            time.sleep(2 ** attempt)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            if attempt == max_attempts - 1:
                return None
            time.sleep(2 ** attempt)

    return None


def extract_country_from_text(value):
    """Infer a country from explicit country words in a label/description."""
    normalized = normalize_lookup_text(value)
    if normalized is None:
        return None

    for alias, country in sorted(
        COUNTRY_ALIAS_MAP.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    ):
        if re.search(rf"\b{re.escape(alias)}\b", normalized):
            return country
    return None


def looks_like_lookup_candidate(agency_name):
    """Skip obvious non-agency strings before calling the network."""
    normalized = normalize_lookup_text(agency_name)
    if normalized is None:
        return False
    if normalized in PLACEHOLDER_VALUES or normalized in AGENCY_NON_VALUES:
        return False
    if "http " in normalized or "https " in normalized or "www " in normalized:
        return False
    if re.match(r"^\d{4}\b", normalized):
        return False
    if re.match(r"^\d+\b", normalized):
        return any(hint in normalized.split() for hint in ORGANIZATION_HINTS)

    words = normalized.split()
    if any(hint in words for hint in ORGANIZATION_HINTS):
        return True
    if any(hint in words for hint in NON_AGENCY_HINTS):
        return False

    stripped = clean_text(agency_name) or ""
    stripped = stripped.strip(" .;,:()")
    if re.fullmatch(r"[A-Z0-9/&.\-]{2,15}", stripped):
        return True

    return len(words) <= 5 and stripped.istitle()


def get_wikidata_entity(entity_id):
    """Fetch and cache a single Wikidata entity payload."""
    if entity_id in WIKIDATA_ENTITY_CACHE:
        return WIKIDATA_ENTITY_CACHE[entity_id]

    url = f"https://www.wikidata.org/wiki/Special:EntityData/{entity_id}.json"
    data = fetch_wikidata_json(url)
    if data is None:
        return None

    entity = data.get("entities", {}).get(entity_id)
    if entity is not None:
        WIKIDATA_ENTITY_CACHE[entity_id] = entity
    return entity


def get_wikidata_label(entity_id):
    """Return the English label for a Wikidata entity ID."""
    entity = get_wikidata_entity(entity_id)
    if entity is None:
        return None

    labels = entity.get("labels", {})
    if "en" in labels:
        return labels["en"]["value"]
    if labels:
        return next(iter(labels.values()))["value"]
    return None


def extract_country_from_location(entity_id, depth=0, seen=None):
    """Resolve a country by following a location entity's country fields."""
    if entity_id is None or depth > 3:
        return None

    if seen is None:
        seen = set()
    if entity_id in seen:
        return None
    seen.add(entity_id)

    entity = get_wikidata_entity(entity_id)
    if entity is None:
        return None

    claims = entity.get("claims", {})
    for property_id in WIKIDATA_ENTITY_COUNTRY_PROPERTIES:
        for claim in claims.get(property_id, []):
            claim_value = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(claim_value, dict) and claim_value.get("id"):
                return get_wikidata_label(claim_value["id"])

    for property_id in ("P131", "P276", "P361"):
        for claim in claims.get(property_id, [])[:3]:
            claim_value = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if not isinstance(claim_value, dict) or claim_value.get("id") is None:
                continue
            country_name = extract_country_from_location(
                claim_value["id"],
                depth=depth + 1,
                seen=seen,
            )
            if country_name is not None:
                return country_name

    return None


def extract_country_from_entity(entity):
    """Read the best country value from a Wikidata entity."""
    claims = entity.get("claims", {})

    for property_id in WIKIDATA_ENTITY_COUNTRY_PROPERTIES:
        for claim in claims.get(property_id, []):
            claim_value = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(claim_value, dict) and claim_value.get("id"):
                country_name = get_wikidata_label(claim_value["id"])
                if country_name is not None:
                    return country_name

    for property_id in WIKIDATA_LOCATION_PROPERTIES:
        for claim in claims.get(property_id, [])[:3]:
            claim_value = claim.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if not isinstance(claim_value, dict) or claim_value.get("id") is None:
                continue
            country_name = extract_country_from_location(claim_value["id"])
            if country_name is not None:
                return country_name

    return None


def score_wikidata_candidate(agency_name, search_result):
    """Score how well a Wikidata search result matches the agency name."""
    normalized_name = normalize_lookup_text(agency_name) or ""
    normalized_label = normalize_lookup_text(search_result.get("label")) or ""
    normalized_aliases = {
        normalize_lookup_text(alias)
        for alias in search_result.get("aliases", []) or []
    }
    normalized_aliases.discard(None)

    combined_terms = " ".join(
        part
        for part in (
            search_result.get("label", ""),
            " ".join(search_result.get("aliases", []) or []),
            search_result.get("description", ""),
        )
        if part
    )
    normalized_combined = normalize_lookup_text(combined_terms) or ""

    score = 0.0
    if normalized_name == normalized_label:
        score += 1.0
    elif normalized_name in normalized_aliases:
        score += 0.9
    elif search_result.get("match", {}).get("type") in {"label", "alias"}:
        score += 0.25

    if normalized_name and normalized_label:
        name_tokens = set(normalized_name.split())
        label_tokens = set(normalized_label.split())
        combined_tokens = set(normalized_combined.split())
        if name_tokens and label_tokens:
            score += 0.4 * len(name_tokens & label_tokens) / len(name_tokens | label_tokens)
        if name_tokens and combined_tokens:
            score += 0.2 * len(name_tokens & combined_tokens) / len(name_tokens | combined_tokens)

    return score


def search_wikidata_for_country(agency_name):
    """Query Wikidata for a country when heuristics are insufficient."""
    variants = []
    cleaned = clean_text(agency_name)
    if cleaned is None:
        return None

    variants.append(cleaned)
    without_parentheses = re.sub(r"\s*\([^)]*\)", "", cleaned).strip(" .;,:")
    if without_parentheses and without_parentheses not in variants:
        variants.append(without_parentheses)

    for variant in variants:
        cache_key = normalize_lookup_text(variant)
        if cache_key in WIKIDATA_SEARCH_CACHE:
            search_results = WIKIDATA_SEARCH_CACHE[cache_key]
        else:
            url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
                {
                    "action": "wbsearchentities",
                    "search": variant,
                    "language": "en",
                    "format": "json",
                    "limit": 5,
                }
            )
            payload = fetch_wikidata_json(url)
            search_results = (payload or {}).get("search", [])
            WIKIDATA_SEARCH_CACHE[cache_key] = search_results

        best_result = None
        best_score = 0.0
        for search_result in search_results:
            candidate_score = score_wikidata_candidate(agency_name, search_result)
            if candidate_score > best_score:
                best_score = candidate_score
                best_result = search_result

        if best_result is None or best_score < 0.45:
            continue

        country_name = extract_country_from_text(best_result.get("description"))
        if country_name is not None:
            return country_name

        entity = get_wikidata_entity(best_result["id"])
        if entity is None:
            continue

        country_name = extract_country_from_entity(entity)
        if country_name is not None:
            return country_name

    return None


def resolve_agency_country(agency_name):
    """Determine a country for an agency name using heuristics then Wikidata."""
    normalized = normalize_lookup_text(agency_name)
    if normalized is None:
        return None
    if normalized in PLACEHOLDER_VALUES or normalized in AGENCY_NON_VALUES:
        return None

    if normalized in AGENCY_COUNTRY_OVERRIDES:
        return AGENCY_COUNTRY_OVERRIDES[normalized]

    inferred_country = extract_country_from_text(agency_name)
    if inferred_country is not None:
        return inferred_country

    if not looks_like_lookup_candidate(agency_name):
        return None

    return search_wikidata_for_country(agency_name)


with open("data_output.json") as f:
    all_data = json.load(f)

connection = mysql.connector.connect(host="localhost", user="root")
cursor = connection.cursor()

# Rebuild the schema on each run so the load starts from a known clean state.
with open("schema.sql", "r") as f:
    for statement in f.read().split(";"):
        statement = statement.strip()
        if statement:
            cursor.execute(statement)

connection.commit()
cursor.close()
connection.close()

connection = mysql.connector.connect(
    user="root",
    host="localhost",
    database="final_project"
)
cursor = connection.cursor()


def ensure_agency_country_column():
    """Add the agencies.country column when schema.sql does not define it."""
    cursor.execute("SHOW COLUMNS FROM agencies LIKE 'country'")
    if cursor.fetchone() is None:
        cursor.execute(
            """
            ALTER TABLE agencies
            ADD COLUMN country VARCHAR(128) NULL AFTER agency_name
            """
        )


def get_agency_id(agency_name):
    """Return an agency ID, inserting the agency row if needed."""
    agency_name = clean_and_remove_placeholder(agency_name)
    if agency_name is None:
        return None

    cursor.execute(
        """
        INSERT IGNORE INTO agencies (agency_name) # we can do this because we make unique key (that also auto creates index)
        VALUES (%s)
        """,
        (agency_name,)
    )
    cursor.execute(
        "SELECT agency_id FROM agencies WHERE agency_name = %s",
        (agency_name,)
    )
    return cursor.fetchone()[0]


def populate_agency_countries():
    """Fill agencies.country for rows where the country can be resolved."""
    cursor.execute(
        """
        SELECT agency_id, agency_name
        FROM agencies
        WHERE country IS NULL OR TRIM(country) = ''
        ORDER BY agency_id
        """
    )
    agencies = cursor.fetchall()

    updated_rows = 0
    print(f"Checking country data for {len(agencies)} agencies...", flush=True)
    for agency_id, agency_name in agencies:
        country_name = resolve_agency_country(agency_name)
        if country_name is None:
            continue

        cursor.execute(
            """
            UPDATE agencies
            SET country = %s
            WHERE agency_id = %s
            """,
            (country_name, agency_id),
        )
        updated_rows += 1

        if updated_rows and updated_rows % 25 == 0:
            connection.commit()
            print(f"Populated country for {updated_rows} agencies...", flush=True)

    print(f"Finished populating countries for {updated_rows} agencies.", flush=True)


def get_institution_id(institution_name):
    """Return an institution ID, inserting the institution row if needed."""
    institution_name = clean_and_remove_placeholder(institution_name)
    if institution_name is None:
        return None

    cursor.execute(
        """
        INSERT IGNORE INTO institutions (institution_name)
        VALUES (%s)
        """,
        (institution_name,)
    )
    cursor.execute(
        "SELECT institution_id FROM institutions WHERE institution_name = %s",
        (institution_name,)
    )
    return cursor.fetchone()[0]


def get_continent_id(continent_name):
    """Return a continent ID, inserting the continent row if needed."""
    continent_name = clean_text(continent_name)
    if continent_name is None:
        return None

    cursor.execute(
        """
        INSERT IGNORE INTO continents (continent_name)
        VALUES (%s)
        """,
        (continent_name,)
    )
    cursor.execute(
        "SELECT continent_id FROM continents WHERE continent_name = %s",
        (continent_name,)
    )
    return cursor.fetchone()[0]


def get_country_id(country_name):
    """Return a country ID, inserting the country row if needed."""
    country_name = clean_text(country_name)
    if country_name is None:
        return None

    cursor.execute(
        """
        INSERT IGNORE INTO countries (country_name)
        VALUES (%s)
        """,
        (country_name,)
    )
    cursor.execute(
        "SELECT country_id FROM countries WHERE country_name = %s",
        (country_name,)
    )
    return cursor.fetchone()[0]


def get_language_id(language_name):
    """Return a language ID, inserting the language row if needed."""
    language_name = clean_and_remove_placeholder(language_name)
    if language_name is None:
        return None

    cursor.execute(
        """
        INSERT IGNORE INTO languages (language_name)
        VALUES (%s)
        """,
        (language_name,)
    )
    cursor.execute(
        "SELECT language_id FROM languages WHERE language_name = %s",
        (language_name,)
    )
    return cursor.fetchone()[0]


ensure_agency_country_column()


for record in all_data:
    record_id = record.get("id")

    cursor.execute(
        """
        INSERT IGNORE INTO records (
            record_id,
            product_type,
            title,
            year_of_publication,
            sector_name,
            abstract,
            evaluation_design,
            evaluation_method
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            record_id,
            record.get("product_type"),
            record.get("title"),
            record.get("year_of_publication"),
            record.get("sector_name"),
            record.get("abstract"),
            record.get("evaluation_design"),
            record.get("evaluation_method"),
        )
    )

    # Store explicit positions so exports can preserve source ordering.
    for author_position, author in enumerate(record.get("authors"), start=1):
        author_name = clean_text(author.get("author"))
        if author_name is None:
            continue

        cursor.execute(
            """
            INSERT INTO recordauthors (
                record_id,
                author_position,
                author_name
            )
            VALUES (%s, %s, %s)
            """,
            (record_id, author_position, author_name),
        )
        record_author_id = cursor.lastrowid

        institution_position = 0
        for institution in author.get("institutions"):
            institution_id = get_institution_id(
                institution.get("author_affiliation")
            )
            institution_country = clean_and_remove_placeholder(
                institution.get("author_country")
            )

            # Some source rows have a country but no institution name.
            if institution_id is None and institution_country is None:
                continue

            institution_position += 1
            cursor.execute(
                """
                INSERT INTO recordauthorinstitutions (
                    record_author_id,
                    institution_position,
                    institution_id,
                    institution_country
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    record_author_id,
                    institution_position,
                    institution_id,
                    institution_country,
                )
            )

    if record.get("language") is not None:
        for language in record.get("language"):
            language_id = get_language_id(language)
            if language_id is None:
                continue

            cursor.execute(
                """
                INSERT IGNORE INTO recordlanguages (record_id, language_id)
                VALUES (%s, %s)
                """,
                (record_id, language_id)
            )

    record_continent_position = 0
    for continent_entry in record.get("continent"):
        continent_id = get_continent_id(continent_entry.get("continent"))
        if continent_id is None:
            continue

        record_continent_position += 1
        cursor.execute(
            """
            INSERT INTO recordcontinents (
                record_id,
                record_continent_position,
                continent_id
            )
            VALUES (%s, %s, %s)
            """,
            (record_id, record_continent_position, continent_id)
        )
        record_continent_id = cursor.lastrowid

        record_country_position = 0
        for country in continent_entry.get("countries"):
            country_id = get_country_id(country.get("country"))
            fcv_status = clean_text(country.get("fcv_status")) # If same country have different attributes across record, we respect the source data
            income_level = clean_text(country.get("income_level"))

            if country_id is None:
                continue

            record_country_position += 1
            cursor.execute(
                """
                INSERT INTO recordcountries (
                    record_continent_id,
                    record_country_position,
                    country_id,
                    fcv_status,
                    income_level
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    record_continent_id,
                    record_country_position,
                    country_id,
                    fcv_status,
                    income_level,
                )
            )

    inserted_research_funder = False
    for project in record.get("project_name") or []: # project_name is null in 1720 records, crash if no "or []"
        for agency in project.get("research_funding_agencies"):
            agency_id = get_agency_id(agency.get("agency_name"))
            if agency_id is None:
                continue

            inserted_research_funder = True
            cursor.execute(
                """
                INSERT IGNORE INTO recordresearchfundingagencies (
                    record_id,
                    agency_id
                )
                VALUES (%s, %s)
                """,
                (record_id, agency_id)
            )

    if not inserted_research_funder: # for srr and egm, this is only available in top-level
        for agency in record.get("research_funding_agency") or []: # research_funding_agency is null in 2,1807 records, crash if no "or []"
            agency_id = get_agency_id(agency.get("agency_name"))
            if agency_id is None:
                continue

            cursor.execute(
                """
                INSERT IGNORE INTO recordresearchfundingagencies (
                    record_id,
                    agency_id
                )
                VALUES (%s, %s)
                """,
                (record_id, agency_id)
            )

connection.commit()
populate_agency_countries()
connection.commit()
cursor.close()
connection.close()
