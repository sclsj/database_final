import csv
import os
import mysql.connector
from datetime import datetime

connection = mysql.connector.connect(
    user = 'root',
    host = 'localhost',
    database = 'final_project'
)
cursor = connection.cursor()

OUTPUT_DIR = "./output"
os.makedirs(OUTPUT_DIR, exist_ok = True)
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

SEPARATOR = "|"

def export_query(query: str, filename: str) -> None:
    cursor.execute(query)
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    filepath = os.path.join(OUTPUT_DIR, f"{filename}_{TIMESTAMP}.csv")
    with open(filepath, "w", newline = "", encoding = "utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
        print(f"{filename}: {len(rows)} rows, {len(columns)} columns to {filepath}")


def get_all_tables() -> list[str]:
    cursor.execute("SHOW TABLES")
    return [row[0] for row in cursor.fetchall()]

def build_query(sep: str) -> str:
    return f"""
    SELECT
        p.paper_id,
        p.product_type,
        p.title,
        p.year_of_publication,
        p.sector_name,
        p.abstract,
        p.evaluation_design,
        p.evaluation_method,
 
        GROUP_CONCAT(
            DISTINCT a.author_name
            ORDER BY pa.author_position
            SEPARATOR '{sep}'
        ) AS authors,
 
        GROUP_CONCAT(
            DISTINCT ag_author.agency_name
            SEPARATOR '{sep}'
        ) AS author_affiliations,
 
        GROUP_CONCAT(
            DISTINCT c.country_name
            SEPARATOR '{sep}'
        ) AS countries,
 
        GROUP_CONCAT(
            DISTINCT con.continent_name
            SEPARATOR '{sep}'
        ) AS continents,
 
        GROUP_CONCAT(
            DISTINCT l.language_name
            SEPARATOR '{sep}'
        ) AS languages,
 
        GROUP_CONCAT(
            DISTINCT ag_funder.agency_name
            SEPARATOR '{sep}'
        ) AS research_funding_agencies
 
        FROM papers p
    
        LEFT JOIN paperauthors                 pa        ON p.paper_id     = pa.paper_id
        LEFT JOIN authors                      a         ON pa.author_id   = a.author_id
        LEFT JOIN agencies                     ag_author ON a.agency_id    = ag_author.agency_id
        LEFT JOIN papercountries               pc        ON p.paper_id     = pc.paper_id
        LEFT JOIN countries                    c         ON pc.country_id  = c.country_id
        LEFT JOIN continents                   con       ON c.continent_id = con.continent_id
        LEFT JOIN paperlanguages               pl        ON p.paper_id     = pl.paper_id
        LEFT JOIN languages                    l         ON pl.language_id = l.language_id
        LEFT JOIN paperresearchfundingagencies prf       ON p.paper_id     = prf.paper_id
        LEFT JOIN agencies                     ag_funder ON prf.agency_id  = ag_funder.agency_id
    
        GROUP BY
            p.paper_id,
            p.product_type,
            p.title,
            p.year_of_publication,
            p.sector_name,
            p.abstract,
            p.evaluation_design,
            p.evaluation_method
    
        ORDER BY p.paper_id
    """
    
tables = get_all_tables()
print(f"Find {len(tables)} tables: {', '.join(tables)}\n")

export_query(build_query(SEPARATOR), "Analysis_table")

cursor.close()
connection.close()

print(f"All tables exported at path ./output/")