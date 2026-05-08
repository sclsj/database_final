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


def get_or_create_agency(agency_name):
    agency_name = normalize_meaningful_text(agency_name)
    if agency_name is None:
        return None

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
    return cursor.fetchone()[0]


def get_or_create_institution(institution_name):
    institution_name = normalize_meaningful_text(institution_name)
    if institution_name is None:
        return None

    cursor.execute(
        """
        INSERT IGNORE INTO institutions (institution_name)
        VALUES (%s)
        """,
        (institution_name,),
    )
    cursor.execute(
        "SELECT institution_id FROM institutions WHERE institution_name = %s",
        (institution_name,),
    )
    return cursor.fetchone()[0]


def get_or_create_continent(continent_name):
    continent_name = normalize_text(continent_name)
    if continent_name is None:
        return None

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
    return cursor.fetchone()[0]


def get_or_create_country(country_name):
    country_name = normalize_text(country_name)
    if country_name is None:
        return None

    cursor.execute(
        """
        INSERT IGNORE INTO countries (country_name)
        VALUES (%s)
        """,
        (country_name,),
    )
    cursor.execute(
        "SELECT country_id FROM countries WHERE country_name = %s",
        (country_name,),
    )
    return cursor.fetchone()[0]


def get_or_create_language(language_name):
    language_name = normalize_meaningful_text(language_name)
    if language_name is None:
        return None

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
    return cursor.fetchone()[0]


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
        ),
    )

    for author_position, author in enumerate(record.get("authors") or [], start=1):
        author_name = normalize_text(author.get("author"))
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
        for institution in author.get("institutions") or []:
            institution_id = get_or_create_institution(
                institution.get("author_affiliation")
            )
            institution_country = normalize_meaningful_text(
                institution.get("author_country")
            )

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
                ),
            )

    if record.get("language") is not None:
        for language in record.get("language") or []:
            language_id = get_or_create_language(language)
            if language_id is None:
                continue

            cursor.execute(
                """
                INSERT IGNORE INTO recordlanguages (record_id, language_id)
                VALUES (%s, %s)
                """,
                (record_id, language_id),
            )

    record_continent_position = 0
    for continent_entry in record.get("continent") or []:
        continent_id = get_or_create_continent(continent_entry.get("continent"))
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
            (record_id, record_continent_position, continent_id),
        )
        record_continent_id = cursor.lastrowid

        record_country_position = 0
        for country in continent_entry.get("countries") or []:
            country_id = get_or_create_country(country.get("country"))
            fcv_status = normalize_text(country.get("fcv_status"))
            income_level = normalize_text(country.get("income_level"))

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
                ),
            )

    inserted_research_funder = False
    for project in record.get("project_name") or []:
        for agency in project.get("research_funding_agencies") or []:
            agency_id = get_or_create_agency(agency.get("agency_name"))
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
                (record_id, agency_id),
            )

    if not inserted_research_funder:
        for agency in record.get("research_funding_agency", []):
            agency_id = get_or_create_agency(agency.get("agency_name"))
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
                (record_id, agency_id),
            )

connection.commit()
cursor.close()
connection.close()
