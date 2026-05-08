# 3ie Final Project

This project builds a small ETL pipeline around 3ie research records:

1. `scraper.py` fetches records from the 3ie GraphQL API and writes them to `data_output.json`.
2. `schema.sql` creates the MySQL database and all tables used by the project.
3. `connector.py` loads `data_output.json` into the relational schema in MySQL.
4. `csv_converter.py` exports selected records from MySQL into a timestamped CSV file.

The project focuses on three 3ie product types:

- `ier`: Independent Evaluation
- `srr`: Systematic Review
- `egm`: Evidence Gap Map

## Project Workflow

The intended run order is:

```bash
python scraper.py
python connector.py
python csv_converter.py
```

At a high level:

- The scraper pulls raw records from `https://api.developmentevidence.3ieimpact.org/graphql`.
- The connector recreates the database schema from `schema.sql`, normalizes the JSON data, and inserts it into related tables.
- The CSV exporter queries the normalized schema and flattens it back into a single-row-per-record CSV.

## Requirements

The code uses:

- Python 3
- `requests`
- `mysql-connector-python`
- A local MySQL server

The Python scripts assume a MySQL user of `root` on `localhost` and do not specify a password in code.

## File Overview

### `scraper.py`

`scraper.py` is the extraction step.

What it does:

- Sends GraphQL POST requests to the 3ie API.
- Requests record metadata, authors, author institutions, project funding information, continents, and countries.
- Fetches records in pages of `200`.
- Repeats the request for each supported product type: `ier`, `srr`, and `egm`.
- Combines all fetched records into a single list.
- Replaces any existing `data_output.json` and writes the fresh API output there.

Important behavior:

- The script sorts results by `recent`.
- It is intentionally not resumable; the comment in the file notes that records can change and the API does not support diff-based updates.
- Output is written as formatted UTF-8 JSON with `ensure_ascii=False`.

Primary output:

- `data_output.json`

### `schema.sql`

`schema.sql` is the database definition for the project.

What it does:

- Creates the `final_project` database if it does not already exist.
- Switches to that database with `USE final_project`.
- Drops all project tables in dependency-safe order.
- Recreates the normalized schema with primary keys, unique keys, and foreign keys.

Important behavior:

- Running the schema file resets the project tables because it drops and recreates them.
- `connector.py` executes this file before loading data, so importing data is a destructive refresh of the database contents.

### `connector.py`

`connector.py` is the transformation and load step.

What it does:

- Reads `data_output.json`.
- Connects to MySQL and executes every statement in `schema.sql`.
- Reconnects to the `final_project` database.
- Inserts core records into `records`.
- Normalizes repeated values into lookup tables such as agencies, institutions, continents, countries, and languages.
- Populates bridge/detail tables for:
  - authors
  - author institutions
  - record continents
  - record countries
  - record languages
  - research funding agencies

Data cleaning rules:

- `clean_text()` collapses whitespace and converts empty strings to `None`.
- `clean_and_remove_placeholder()` also removes placeholder values such as:
  - `not specified`
  - `not reported`
  - `not applicable`
  - `n/a`
  - `none`
  - `not available`

Important behavior:

- Agencies, institutions, continents, countries, and languages are inserted with `INSERT IGNORE` and then re-selected, so duplicate dimension values are reused.
- Author order, institution order, continent order, and country order are preserved using explicit position columns.
- Research funding agencies are loaded from nested project data first. If none are found there, the loader falls back to the top-level `research_funding_agency` field because the source data is inconsistent about where funding information is stored.
- The script commits once at the end.

### `csv_converter.py`

`csv_converter.py` is the reporting/export step.

What it does:

- Prompts the user for which record types to export.
- Connects to the `final_project` database.
- Runs a SQL query that joins and aggregates the normalized tables back into a flat export format.
- Writes the results to `./output/record_export_<timestamp>.csv`.

Exported columns:

- `record_id`
- `product_type`
- `title`
- `year_of_publication`
- `sector_name`
- `evaluation_design`
- `evaluation_method`
- `authors`
- `author_institutions`
- `author_countries`
- `record_countries`
- `record_continents`
- `languages`
- `research_funding_agencies`

Formatting choices:

- Multiple top-level values are joined with `|`.
- Multiple values within a single author field are joined with `;`.
- Files are written with `utf-8-sig`, which helps Excel open the CSV correctly.
- Output files are timestamped and saved under `./output`.

Important behavior:

- The script raises `group_concat_max_len` to avoid truncating long aggregated fields.
- It exports one row per record.

## Database Schema

The schema is normalized around a central `records` table.

### Core table

- `records`: one row per 3ie record, with basic metadata such as product type, title, year, sector, abstract, evaluation design, and evaluation method.

### Lookup tables

- `agencies`: unique research funding agency names
- `institutions`: unique institution names
- `continents`: unique continent names
- `countries`: unique country names
- `languages`: unique language names

### Relationship and detail tables

- `recordauthors`: authors for a record, including author order
- `recordauthorinstitutions`: institutions and institution-country values for each author, including institution order
- `recordcontinents`: continents associated with a record, including continent order
- `recordcountries`: countries associated with a record continent, including country order plus `fcv_status` and `income_level`
- `recordlanguages`: many-to-many link between records and languages
- `recordresearchfundingagencies`: many-to-many link between records and agencies

## Table Relationships

The main relationships are:

- One `records` row can have many `recordauthors`.
- One `recordauthors` row can have many `recordauthorinstitutions`.
- One `records` row can have many `recordcontinents`.
- One `recordcontinents` row can have many `recordcountries`.
- One `records` row can have many `recordlanguages`.
- One `records` row can have many `recordresearchfundingagencies`.

This design avoids repeating agency, institution, country, continent, and language names across every record.

## How Data Moves Through the Project

### 1. Extraction

The scraper collects raw API responses for the three supported product types and stores them as a JSON snapshot.

### 2. Normalization

The connector reads that JSON and separates repeated entities into lookup tables while preserving ordering for authors, institutions, continents, and countries.

### 3. Flattened export

The CSV converter reconstructs a report-friendly format by aggregating related rows with `GROUP_CONCAT`.

## Source Data Quirks

Some of the Python logic exists specifically to handle irregular API data rather than idealized clean records.

- `project_name` is `null` in `1,720` records, so `connector.py` uses `or []` before iterating.
- `research_funding_agency` is `null` in `21,807` records, so the same defensive pattern is used there.
- The funding source is not stored consistently. In the JSON snapshot, `892` records have usable top-level `research_funding_agency` values while `project_name` is `null`, so the loader has a fallback branch instead of assuming all funding data is nested under projects.
- Some author institution entries contain a country but no institution name. The JSON snapshot includes `39` records with at least one such case, which is why `recordauthorinstitutions` allows `institution_id` to be `NULL` while still storing `institution_country`.
- Placeholder text is used in the source instead of true nulls for some fields. The loader explicitly treats values such as `not specified`, `not reported`, `not applicable`, `n/a`, `unspecified`, `none`, and `not available` as missing data.

These quirks explain why parts of the loader are more defensive than the schema alone might suggest.

## Operational Notes and Assumptions

- The database name is fixed as `final_project`.
- The scripts are written for a local MySQL instance on `localhost`.
- `connector.py` rebuilds the schema before loading data, so rerunning it replaces previously loaded project data.
- `csv_converter.py` is interactive because it asks which product types to export.
- `data_output.json` must exist before `connector.py` is run.

## Suggested Usage

If starting from scratch:

1. Run `scraper.py` to generate `data_output.json`.
2. Run `connector.py` to rebuild and populate the MySQL database.
3. Run `csv_converter.py` and choose either all record types or a comma-separated subset.
4. Check the generated CSV in the `output/` directory.

## Summary

This project turns 3ie evidence records into a normalized MySQL database and then into a flat CSV export. The design separates extraction, loading, and exporting into three scripts, with `schema.sql` defining the relational structure that connects them.
