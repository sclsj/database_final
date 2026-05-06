import json

import mysql.connector


PLACEHOLDER_VALUES = {"", "not specified", "not applicable"}


def normalize_text(value):
    if value is None:
        return None

    cleaned = " ".join(str(value).split()).strip()
    return cleaned or None


def normalize_meaningful_text(value):
    cleaned = normalize_text(value)
    if cleaned is None:
        return None
    if cleaned.lower() in PLACEHOLDER_VALUES:
        return None
    return cleaned


def first_meaningful_affiliation(author_entry):
    for institution in author_entry.get("institutions") or []:
        affiliation = normalize_meaningful_text(
            institution.get("author_affiliation")
        )
        return affiliation


def first_author_country(author_entry):
    for institution in author_entry.get("institutions") or []:
        author_country = normalize_meaningful_text(
            institution.get("author_country")
        )
        return author_country


with open("data_output.json") as f:
    all_data = json.load(f)

connection = mysql.connector.connect(host="localhost", user="root")
cursor = connection.cursor()

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
    database="final_project",
)
cursor = connection.cursor()

agency_cache = {}
author_cache = {}
continent_cache = {}
country_cache = {}
language_cache = {}


def get_or_create_agency(agency_name):
    agency_name = normalize_meaningful_text(agency_name)
    if agency_name is None:
        return None

    if agency_name in agency_cache:
        return agency_cache[agency_name]

    cursor.execute(
        """
        INSERT IGNORE INTO agencies (agency_name)
        VALUES (%s)
        """,
        (agency_name,),
    )
    cursor.execute(
        "SELECT agency_id FROM agencies WHERE agency_name = %s",
        (agency_name,),
    )
    agency_id = cursor.fetchone()[0]
    agency_cache[agency_name] = agency_id
    return agency_id


def get_or_create_author(author_name, agency_id, author_country):
    author_name = normalize_text(author_name)
    if author_name is None:
        return None

    if author_name in author_cache:
        return author_cache[author_name]

    cursor.execute(
        """
        INSERT IGNORE INTO authors (author_name, agency_id, author_country)
        VALUES (%s, %s, %s)
        """,
        (author_name, agency_id, author_country),
    )
    cursor.execute(
        "SELECT author_id FROM authors WHERE author_name = %s",
        (author_name,),
    )
    author_id = cursor.fetchone()[0]
    author_cache[author_name] = author_id
    return author_id


def get_or_create_continent(continent_name):
    continent_name = normalize_text(continent_name)
    if continent_name is None:
        return None

    if continent_name in continent_cache:
        return continent_cache[continent_name]

    cursor.execute(
        """
        INSERT IGNORE INTO continents (continent_name)
        VALUES (%s)
        """,
        (continent_name,),
    )
    cursor.execute(
        "SELECT continent_id FROM continents WHERE continent_name = %s",
        (continent_name,),
    )
    continent_id = cursor.fetchone()[0]
    continent_cache[continent_name] = continent_id
    return continent_id


def get_or_create_country(country_name, continent_id, fcv_status, income_level):
    country_name = normalize_text(country_name)
    if country_name is None:
        return None

    fcv_status = normalize_text(fcv_status)
    income_level = normalize_text(income_level)

    if country_name in country_cache:
        country_id = country_cache[country_name] # sometimes fcv and inco
        cursor.execute(
            """
            UPDATE countries
            SET
                continent_id = COALESCE(continent_id, %s),
                fcv_status = COALESCE(fcv_status, %s),
                income_level = COALESCE(income_level, %s)
            WHERE country_id = %s
            """,
            (continent_id, fcv_status, income_level, country_id),
        )
        return country_id

    cursor.execute(
        """
        INSERT IGNORE INTO countries (
            country_name,
            continent_id,
            fcv_status,
            income_level
        )
        VALUES (%s, %s, %s, %s)
        """,
        (country_name, continent_id, fcv_status, income_level),
    )
    cursor.execute(
        "SELECT country_id FROM countries WHERE country_name = %s",
        (country_name,),
    )
    country_id = cursor.fetchone()[0]
    country_cache[country_name] = country_id
    return country_id


def get_or_create_language(language_name):
    language_name = normalize_meaningful_text(language_name)
    if language_name is None:
        return None

    if language_name in language_cache:
        return language_cache[language_name]

    cursor.execute(
        """
        INSERT IGNORE INTO languages (language_name)
        VALUES (%s)
        """,
        (language_name,),
    )
    cursor.execute(
        "SELECT language_id FROM languages WHERE language_name = %s",
        (language_name,),
    )
    language_id = cursor.fetchone()[0]
    language_cache[language_name] = language_id
    return language_id


for paper in all_data:
    paper_id = paper.get("id")

    cursor.execute(
        """
        INSERT IGNORE INTO papers (
            paper_id,
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
            paper_id,
            paper.get("product_type"),
            paper.get("title"),
            paper.get("year_of_publication"),
            paper.get("sector_name"),
            paper.get("abstract"),
            paper.get("evaluation_design"),
            paper.get("evaluation_method"),
        ),
    )

    for position, author in enumerate(paper.get("authors") or [], start=1):
        author_name = normalize_text(author.get("author"))
        if author_name is None:
            continue

        agency_id = get_or_create_agency(first_meaningful_affiliation(author))
        author_country = first_author_country(author)
        author_id = get_or_create_author(
            author_name,
            agency_id,
            author_country,
        )

        cursor.execute(
            """
            INSERT IGNORE INTO paperauthors (
                paper_id,
                author_position,
                author_id
            )
            VALUES (%s, %s, %s)
            """,
            (paper_id, position, author_id),
        )
    if paper.get("language", []) is not None:
        for language in paper.get("language", []):
            language_id = get_or_create_language(language)
            if language_id is None:
                continue

            cursor.execute(
                """
                INSERT IGNORE INTO paperlanguages (paper_id, language_id)
                VALUES (%s, %s)
                """,
                (paper_id, language_id),
            )

    for continent_entry in paper.get("continent") or []:
        continent_name = normalize_text(continent_entry.get("continent"))
        if continent_name is None:
            continue

        continent_id = get_or_create_continent(continent_name)
        cursor.execute(
            """
            INSERT IGNORE INTO papercontinents (paper_id, continent_id)
            VALUES (%s, %s)
            """,
            (paper_id, continent_id),
        )

        for country in continent_entry.get("countries") or []:
            country_id = get_or_create_country(
                country.get("country"),
                continent_id,
                country.get("fcv_status"),
                country.get("income_level"),
            )
            if country_id is None:
                continue

            cursor.execute(
                """
                INSERT IGNORE INTO papercountries (paper_id, country_id)
                VALUES (%s, %s)
                """,
                (paper_id, country_id),
            )

    inserted_research_funder = False
    for project in paper.get("project_name") or []:
        for agency in project.get("research_funding_agencies") or []:
            agency_id = get_or_create_agency(agency.get("agency_name"))
            if agency_id is None:
                continue

            inserted_research_funder = True
            cursor.execute(
                """
                INSERT IGNORE INTO paperresearchfundingagencies (
                    paper_id,
                    agency_id
                )
                VALUES (%s, %s)
                """,
                (paper_id, agency_id),
            )

    if not inserted_research_funder:
        for agency in paper.get("research_funding_agency", []):
            agency_id = get_or_create_agency(agency.get("agency_name"))
            if agency_id is None:
                continue

            cursor.execute(
                """
                INSERT IGNORE INTO paperresearchfundingagencies (
                    paper_id,
                    agency_id
                )
                VALUES (%s, %s)
                """,
                (paper_id, agency_id),
            )

connection.commit()
cursor.close()
connection.close()
