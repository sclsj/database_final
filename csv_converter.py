"""
This is a command-line tool for exporting 3ie research records from a mySQL
database to a CSV file.

This tool supports three record types:
    ier: Indenpendent Evaluation
    srr: Systematic Review
    egm: Evidence Gap Map

Exported fields include the core record data, authors with their affiliated
institutions, countries of the study, countries of the authors, languages,
and research funding agencies.

Output files are saved to ./output/ with a timestamp appended to the filename.
Files are encoded in UTF-8.
    
"""
import csv
import os
from datetime import datetime

import mysql.connector


OUTPUT_DIR = "./output"
DEFAULT_STUDY_TYPES = ["ier", "srr", "egm"]

# Coulmns included for the exported data
DEFAULT_COLUMNS = [
    "record_id",
    "product_type",
    "title",
    "year_of_publication",
    "sector_name",
    "evaluation_design",
    "evaluation_method",
    "authors",
    "author_institutions",
    "author_countries",
    "record_countries",
    "record_continents",
    "languages",
    "research_funding_agencies",
]

def ask_study_type():
    """
    This program prompts the user to select which record types to export.

    If the user answers "yes", all default types (ier, srr, egm) are returned.
    If the user answers "no", they are prompted to enter one or more types
    using comma as the separator.

    """
    answer = input("Export all record types (ier, srr, egm)? [yes/no]").strip().lower()
    if answer == "yes":
        return DEFAULT_STUDY_TYPES
    else:
        raw = input("Please input the record type(s) for export, using ',' to separate (e.g. ier, srr):").strip()
        types = [t.strip() for t in raw.split(",") if t.strip()]
        if not types:
            raise ValueError("Please enter at least one record type.")
        return types

# Build a SQL placeholder string from a list of values using %s
def build_in_clause(values):
    placeholders = ", ".join(["%s"] * len(values))
    return f"({placeholders})"


def fetch_all_rows(cursor, study_types, list_separator, within_author_separator):
    """
    Here, the main query is executed to fetch all records of the specified type(s).
    All their associated data are aggregated into a single-row results.
    """

    study_types_clause = build_in_clause(study_types)
    query = """
        SELECT
            r.record_id,
            r.product_type,
            r.title,
            r.year_of_publication,
            r.sector_name,
            r.evaluation_design,
            r.evaluation_method,
            COALESCE(a.authors, '') AS authors,
            COALESCE(a.author_institutions, '') AS author_institutions,
            COALESCE(a.author_countries, '') AS author_countries,
            COALESCE(g.record_countries, '') AS record_countries,
            COALESCE(g.record_continents, '') AS record_continents,
            COALESCE(l.languages, '') AS languages,
            COALESCE(f.research_funding_agencies, '') AS research_funding_agencies
        FROM records r
        
        LEFT JOIN (
            SELECT
                ra.record_id,
                GROUP_CONCAT(
                    ra.author_name
                    ORDER BY ra.author_position
                    SEPARATOR %s
                ) AS authors,
                GROUP_CONCAT(
                    COALESCE(ai.author_institutions, '')
                    ORDER BY ra.author_position
                    SEPARATOR %s
                ) AS author_institutions,
                GROUP_CONCAT(
                    COALESCE(ai.author_countries, '')
                    ORDER BY ra.author_position
                    SEPARATOR %s
                ) AS author_countries
            FROM recordauthors ra
            LEFT JOIN (
                SELECT
                    rai.record_author_id,
                    GROUP_CONCAT(
                        DISTINCT i.institution_name
                        ORDER BY rai.institution_position
                        SEPARATOR %s
                    ) AS author_institutions,
                    GROUP_CONCAT(
                        DISTINCT rai.institution_country
                        ORDER BY rai.institution_position
                        SEPARATOR %s
                    ) AS author_countries
                FROM recordauthorinstitutions rai
                LEFT JOIN institutions i
                  ON i.institution_id = rai.institution_id
                GROUP BY rai.record_author_id
            ) ai ON ai.record_author_id = ra.record_author_id
            GROUP BY ra.record_id
        ) a ON a.record_id = r.record_id
        LEFT JOIN (
            SELECT
                rc.record_id,
                GROUP_CONCAT(
                    DISTINCT c.continent_name
                    ORDER BY rc.record_continent_position
                    SEPARATOR %s
                ) AS record_continents,
                GROUP_CONCAT(
                    DISTINCT co.country_name
                    ORDER BY rc.record_continent_position,
                             rco.record_country_position
                    SEPARATOR %s
                ) AS record_countries
            FROM recordcontinents rc
            JOIN continents c
              ON c.continent_id = rc.continent_id
            LEFT JOIN recordcountries rco
              ON rco.record_continent_id = rc.record_continent_id
            LEFT JOIN countries co
              ON co.country_id = rco.country_id
            GROUP BY rc.record_id
        ) g ON g.record_id = r.record_id
        LEFT JOIN (
            SELECT
                rl.record_id,
                GROUP_CONCAT(
                    DISTINCT l.language_name
                    ORDER BY l.language_name
                    SEPARATOR %s
                ) AS languages
            FROM recordlanguages rl
            JOIN languages l
              ON l.language_id = rl.language_id
            GROUP BY rl.record_id
        ) l ON l.record_id = r.record_id
        LEFT JOIN (
            SELECT
                rrfa.record_id,
                GROUP_CONCAT(
                    DISTINCT a.agency_name
                    ORDER BY a.agency_name
                    SEPARATOR %s
                ) AS research_funding_agencies
            FROM recordresearchfundingagencies rrfa
            JOIN agencies a
              ON a.agency_id = rrfa.agency_id
            GROUP BY rrfa.record_id
        ) f ON f.record_id = r.record_id
        WHERE r.product_type IN
    """

    query += study_types_clause + " ORDER BY r.record_id"

    # Parameters for each field in order
    params = [
        list_separator,
        list_separator,
        list_separator,
        within_author_separator,
        within_author_separator,
        list_separator,
        list_separator,
        list_separator,
        list_separator,
        *study_types,
    ]
    cursor.execute(query, params)
    
    # Convert each result tuple into a dict keyed by column name for CSV writing
    rows = []
    for row in cursor.fetchall():
        rows.append(dict(zip(DEFAULT_COLUMNS, row)))
    return rows

def write_csv(rows, columns, output_prefix):
    """
    Write a list of records into a timestamped CSV file.
    """
    os.makedirs(OUTPUT_DIR, exist_ok = True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"{output_prefix}_{timestamp}.csv")

    with open(filepath, "w", newline = "", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})

    print(f"Exported {len(rows)} rows and {len(columns)} columns to {filepath}")

def main():
    """
    Main function: user interaction, database connection, data retrieval,
    and CSV export.
    """
    study_types = ask_study_type()
    columns = DEFAULT_COLUMNS
    list_separator = "|"
    within_author_separator = ";"
    output_prefix = "record_export"

    connection = mysql.connector.connect(
        user="root",
        host="localhost",
        database="final_project",
    )
    cursor = connection.cursor()
    
    # needed because group concat is limited to 1024 by default and truncating strings.
    cursor.execute(
        "SET SESSION group_concat_max_len = %s",
        (1024 * 1024,),
    )

    rows = fetch_all_rows(cursor, study_types, list_separator, within_author_separator)

    write_csv(rows, columns, output_prefix)

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()