import argparse
import csv
import os
from collections import defaultdict
from datetime import datetime

import mysql.connector


OUTPUT_DIR = "./output"
DEFAULT_STUDY_TYPES = ["ier", "srr", "egm"]
DEFAULT_AUTHOR_COUNTRY_SOURCE = "institution"
DEFAULT_LIST_SEPARATOR = "|"
DEFAULT_WITHIN_AUTHOR_SEPARATOR = ";"
DEFAULT_COLUMNS = [
    "record_id",
    "product_type",
    "title",
    "year_of_publication",
    "sector_name",
    "abstract",
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
AVAILABLE_COLUMNS = DEFAULT_COLUMNS + [
    "fcv_statuses",
    "income_levels",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export final_project records to CSV."
    )
    parser.add_argument(
        "--study-types",
        default=",".join(DEFAULT_STUDY_TYPES),
        help="Comma-separated record types to export, e.g. ier,srr,egm",
    )
    parser.add_argument(
        "--columns",
        default="default",
        help=(
            "Columns to export: 'default', 'all', or a comma-separated list "
            f"from {', '.join(AVAILABLE_COLUMNS)}"
        ),
    )
    parser.add_argument(
        "--author-country-source",
        choices=["institution", "record"],
        default="institution",
        help=(
            "Use institution_country from author affiliations, or repeat the "
            "record countries for each author slot."
        ),
    )
    parser.add_argument(
        "--list-separator",
        default="|",
        help="Separator for record-level multi-value fields.",
    )
    parser.add_argument(
        "--within-author-separator",
        default=";",
        help=(
            "Separator for multiple values belonging to the same author, "
            "such as multiple institutions or institution countries."
        ),
    )
    parser.add_argument(
        "--output-prefix",
        default="record_export",
        help="Prefix for the output CSV filename.",
    )
    return parser.parse_args()


def parse_csv_list(raw_value):
    return [item.strip() for item in raw_value.split(",") if item.strip()]


def resolve_columns(raw_value):
    lowered = raw_value.strip().lower()
    if lowered == "default":
        return list(DEFAULT_COLUMNS)
    if lowered == "all":
        return list(AVAILABLE_COLUMNS)

    columns = parse_csv_list(raw_value)
    invalid = [column for column in columns if column not in AVAILABLE_COLUMNS]
    if invalid:
        raise ValueError(
            "Unknown columns: "
            + ", ".join(invalid)
            + ". Valid columns are: "
            + ", ".join(AVAILABLE_COLUMNS)
        )
    return columns


def normalize_text(value):
    if value is None:
        return None

    cleaned = " ".join(str(value).split()).strip()
    return cleaned or None


def append_unique(values, value):
    if value is None:
        return
    if value not in values:
        values.append(value)


def join_values(values, separator):
    return separator.join(value for value in values if value is not None)


def build_in_clause(values):
    placeholders = ", ".join(["%s"] * len(values))
    return f"({placeholders})"


def is_default_export_mode(
    columns,
    author_country_source,
    list_separator,
    within_author_separator,
):
    return (
        columns == DEFAULT_COLUMNS
        and author_country_source == DEFAULT_AUTHOR_COUNTRY_SOURCE
        and list_separator == DEFAULT_LIST_SEPARATOR
        and within_author_separator == DEFAULT_WITHIN_AUTHOR_SEPARATOR
    )


def fetch_default_export_rows(
    cursor,
    study_types,
    list_separator,
    within_author_separator,
):
    study_types_clause = build_in_clause(study_types)
    query = """
        SELECT
            r.record_id,
            r.product_type,
            r.title,
            r.year_of_publication,
            r.sector_name,
            r.abstract,
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
            ) ai
              ON ai.record_author_id = ra.record_author_id
            GROUP BY ra.record_id
        ) a
          ON a.record_id = r.record_id
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
                    ORDER BY rc.record_continent_position, rco.record_country_position
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
        ) g
          ON g.record_id = r.record_id
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
        ) l
          ON l.record_id = r.record_id
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
        ) f
          ON f.record_id = r.record_id
        WHERE r.product_type IN """
    query += study_types_clause + """
        ORDER BY r.record_id
    """
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
    rows = []
    expected_column_count = len(DEFAULT_COLUMNS)
    for row in cursor.fetchall():
        if len(row) != expected_column_count:
            raise ValueError(
                "Unexpected default export column count: "
                f"expected {expected_column_count}, got {len(row)}"
            )
        rows.append(dict(zip(DEFAULT_COLUMNS, row)))
    return rows


def fetch_records(cursor, study_types):
    query = f"""
        SELECT
            record_id,
            product_type,
            title,
            year_of_publication,
            sector_name,
            abstract,
            evaluation_design,
            evaluation_method
        FROM records
        WHERE product_type IN {build_in_clause(study_types)}
        ORDER BY record_id
    """
    cursor.execute(query, study_types)
    return cursor.fetchall()


def fetch_author_rows(cursor, study_types):
    query = f"""
        SELECT
            ra.record_id,
            ra.record_author_id,
            ra.author_position,
            ra.author_name,
            rai.institution_position,
            i.institution_name,
            rai.institution_country
        FROM recordauthors ra
        JOIN records r
          ON r.record_id = ra.record_id
        LEFT JOIN recordauthorinstitutions rai
          ON rai.record_author_id = ra.record_author_id
        LEFT JOIN institutions i
          ON i.institution_id = rai.institution_id
        WHERE r.product_type IN {build_in_clause(study_types)}
        ORDER BY
            ra.record_id,
            ra.author_position,
            rai.institution_position
    """
    cursor.execute(query, study_types)
    return cursor.fetchall()


def fetch_continent_rows(cursor, study_types):
    query = f"""
        SELECT
            rc.record_id,
            rc.record_continent_id,
            rc.record_continent_position,
            c.continent_name
        FROM recordcontinents rc
        JOIN records r
          ON r.record_id = rc.record_id
        JOIN continents c
          ON c.continent_id = rc.continent_id
        WHERE r.product_type IN {build_in_clause(study_types)}
        ORDER BY
            rc.record_id,
            rc.record_continent_position
    """
    cursor.execute(query, study_types)
    return cursor.fetchall()


def fetch_country_rows(cursor, study_types):
    query = f"""
        SELECT
            rc.record_id,
            rc.record_continent_id,
            rco.record_country_id,
            rco.record_country_position,
            c.country_name,
            rco.fcv_status,
            rco.income_level
        FROM recordcontinents rc
        JOIN records r
          ON r.record_id = rc.record_id
        JOIN recordcountries rco
          ON rco.record_continent_id = rc.record_continent_id
        JOIN countries c
          ON c.country_id = rco.country_id
        WHERE r.product_type IN {build_in_clause(study_types)}
        ORDER BY
            rc.record_id,
            rc.record_continent_position,
            rco.record_country_position
    """
    cursor.execute(query, study_types)
    return cursor.fetchall()


def fetch_language_rows(cursor, study_types):
    query = f"""
        SELECT
            rl.record_id,
            l.language_name
        FROM recordlanguages rl
        JOIN records r
          ON r.record_id = rl.record_id
        JOIN languages l
          ON l.language_id = rl.language_id
        WHERE r.product_type IN {build_in_clause(study_types)}
        ORDER BY rl.record_id, l.language_name
    """
    cursor.execute(query, study_types)
    return cursor.fetchall()


def fetch_funder_rows(cursor, study_types):
    query = f"""
        SELECT
            rrfa.record_id,
            a.agency_name
        FROM recordresearchfundingagencies rrfa
        JOIN records r
          ON r.record_id = rrfa.record_id
        JOIN agencies a
          ON a.agency_id = rrfa.agency_id
        WHERE r.product_type IN {build_in_clause(study_types)}
        ORDER BY rrfa.record_id, a.agency_name
    """
    cursor.execute(query, study_types)
    return cursor.fetchall()


def build_export_rows(
    record_rows,
    author_rows,
    continent_rows,
    country_rows,
    language_rows,
    funder_rows,
    author_country_source,
    list_separator,
    within_author_separator,
):
    records = {}
    record_order = []

    for row in record_rows:
        (
            record_id,
            product_type,
            title,
            year_of_publication,
            sector_name,
            abstract,
            evaluation_design,
            evaluation_method,
        ) = row
        records[record_id] = {
            "record_id": record_id,
            "product_type": product_type,
            "title": title,
            "year_of_publication": year_of_publication,
            "sector_name": sector_name,
            "abstract": abstract,
            "evaluation_design": evaluation_design,
            "evaluation_method": evaluation_method,
            "authors_data": [],
            "record_continents": [],
            "record_countries": [],
            "fcv_statuses": [],
            "income_levels": [],
            "languages": [],
            "research_funding_agencies": [],
        }
        record_order.append(record_id)

    authors_by_record_author_id = {}
    for row in author_rows:
        (
            record_id,
            record_author_id,
            author_position,
            author_name,
            institution_position,
            institution_name,
            institution_country,
        ) = row
        if record_author_id not in authors_by_record_author_id:
            author_entry = {
                "author_position": author_position,
                "author_name": author_name,
                "institutions": [],
                "institution_countries": [],
            }
            authors_by_record_author_id[record_author_id] = author_entry
            records[record_id]["authors_data"].append(author_entry)
        else:
            author_entry = authors_by_record_author_id[record_author_id]

        append_unique(
            author_entry["institutions"],
            normalize_text(institution_name),
        )
        append_unique(
            author_entry["institution_countries"],
            normalize_text(institution_country),
        )

    for row in continent_rows:
        record_id, _, _, continent_name = row
        append_unique(
            records[record_id]["record_continents"],
            normalize_text(continent_name),
        )

    for row in country_rows:
        (
            record_id,
            _record_continent_id,
            _record_country_id,
            _record_country_position,
            country_name,
            fcv_status,
            income_level,
        ) = row
        append_unique(
            records[record_id]["record_countries"],
            normalize_text(country_name),
        )
        append_unique(
            records[record_id]["fcv_statuses"],
            normalize_text(fcv_status),
        )
        append_unique(
            records[record_id]["income_levels"],
            normalize_text(income_level),
        )

    for record_id, language_name in language_rows:
        append_unique(records[record_id]["languages"], normalize_text(language_name))

    for record_id, agency_name in funder_rows:
        append_unique(
            records[record_id]["research_funding_agencies"],
            normalize_text(agency_name),
        )

    export_rows = []
    for record_id in record_order:
        record = records[record_id]
        authors_data = sorted(
            record["authors_data"],
            key=lambda author: author["author_position"],
        )

        author_names = [
            normalize_text(author["author_name"]) or ""
            for author in authors_data
        ]
        author_institutions = [
            join_values(author["institutions"], within_author_separator)
            for author in authors_data
        ]

        if author_country_source == "institution":
            author_countries = [
                join_values(author["institution_countries"], within_author_separator)
                for author in authors_data
            ]
        else:
            record_country_value = join_values(
                record["record_countries"],
                within_author_separator,
            )
            author_countries = [record_country_value for _ in authors_data]

        export_rows.append(
            {
                "record_id": record["record_id"],
                "product_type": record["product_type"],
                "title": record["title"],
                "year_of_publication": record["year_of_publication"],
                "sector_name": record["sector_name"],
                "abstract": record["abstract"],
                "evaluation_design": record["evaluation_design"],
                "evaluation_method": record["evaluation_method"],
                "authors": join_values(author_names, list_separator),
                "author_institutions": join_values(
                    author_institutions,
                    list_separator,
                ),
                "author_countries": join_values(
                    author_countries,
                    list_separator,
                ),
                "record_countries": join_values(
                    record["record_countries"],
                    list_separator,
                ),
                "record_continents": join_values(
                    record["record_continents"],
                    list_separator,
                ),
                "languages": join_values(record["languages"], list_separator),
                "research_funding_agencies": join_values(
                    record["research_funding_agencies"],
                    list_separator,
                ),
                "fcv_statuses": join_values(
                    record["fcv_statuses"],
                    list_separator,
                ),
                "income_levels": join_values(
                    record["income_levels"],
                    list_separator,
                ),
            }
        )

    return export_rows


def write_csv(rows, columns, output_prefix):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(OUTPUT_DIR, f"{output_prefix}_{timestamp}.csv")

    with open(filepath, "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})

    print(
        f"Exported {len(rows)} rows and {len(columns)} columns to {filepath}"
    )


def main():
    args = parse_args()
    study_types = parse_csv_list(args.study_types)
    if not study_types:
        raise ValueError("At least one study type must be provided.")

    columns = resolve_columns(args.columns)

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

    if is_default_export_mode(
        columns=columns,
        author_country_source=args.author_country_source,
        list_separator=args.list_separator,
        within_author_separator=args.within_author_separator,
    ):
        rows = fetch_default_export_rows(
            cursor=cursor,
            study_types=study_types,
            list_separator=args.list_separator,
            within_author_separator=args.within_author_separator,
        )
    else:
        record_rows = fetch_records(cursor, study_types)
        author_rows = fetch_author_rows(cursor, study_types)
        continent_rows = fetch_continent_rows(cursor, study_types)
        country_rows = fetch_country_rows(cursor, study_types)
        language_rows = fetch_language_rows(cursor, study_types)
        funder_rows = fetch_funder_rows(cursor, study_types)

        rows = build_export_rows(
            record_rows=record_rows,
            author_rows=author_rows,
            continent_rows=continent_rows,
            country_rows=country_rows,
            language_rows=language_rows,
            funder_rows=funder_rows,
            author_country_source=args.author_country_source,
            list_separator=args.list_separator,
            within_author_separator=args.within_author_separator,
        )

    write_csv(rows, columns, args.output_prefix)

    cursor.close()
    connection.close()


if __name__ == "__main__":
    main()
