import argparse
from collections import defaultdict
import json
import re

import requests


API_URL = "https://api.developmentevidence.3ieimpact.org/graphql"
PAGE_SIZE = 200


SEARCH_QUERY = """
query ($data: KeywordSearchInput!) {
  keywordSearch(data: $data) {
    total_count
    search_result {
      id
      title
      authors {
        author
        institutions {
          author_affiliation
        }
      }
    }
  }
}
"""


def normalize_text(value):
    if value is None:
        return None

    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned or None


def fetch_search_page(product_type, start=0, size=PAGE_SIZE):
    variables = {
        "data": {
            "keyword": "",
            "from": start,
            "size": size,
            "sort_by": "recent",
            "filters": {
                "product_type": [product_type],
                "sector_name": [],
                "continents": [],
                "countries": [],
                "primary_theme": [],
                "equity_focus": [],
                "year_of_publication": [],
                "equity_dimension": [],
                "evidence_programme": [],
                "fcv_status": [],
                "dataset_available": [],
                "primary_dac_codes": [],
                "un_sdg": [],
                "primary_dataset_availability": [],
                "pre_registration": [],
                "interventions": [],
                "outcome": [],
                "evaluation_method": [],
                "confidence_level": [],
                "threeie_funded": [],
                "threeie_produced": [],
            },
        }
    }

    response = requests.post(
        API_URL,
        json={"query": SEARCH_QUERY, "variables": variables},
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()
    if "errors" in payload:
        raise RuntimeError(json.dumps(payload["errors"], indent=2))

    return payload["data"]["keywordSearch"]


def fetch_all_records(product_type):
    all_records = []
    start = 0

    first_page = fetch_search_page(product_type, start=start, size=PAGE_SIZE)
    total_count = first_page["total_count"]
    all_records.extend(first_page["search_result"])
    print(f"Fetched {len(all_records)}/{total_count}", flush=True)

    while len(all_records) < total_count:
        start += PAGE_SIZE
        page = fetch_search_page(product_type, start=start, size=PAGE_SIZE)
        records = page["search_result"]
        if not records:
            break

        all_records.extend(records)
        print(f"Fetched {len(all_records)}/{total_count}", flush=True)

    return all_records


def analyze_affiliations(records):
    authors = defaultdict(
        lambda: {
            "affiliations": set(),
            "missing_occurrences": 0,
            "occurrences": 0,
            "paper_examples": [],
        }
    )

    for paper in records:
        paper_id = paper.get("id")
        title = paper.get("title")

        for author_entry in paper.get("authors", []):
            author_name = normalize_text(author_entry.get("author"))
            if not author_name:
                continue

            affiliations = {
                affiliation
                for inst in author_entry.get("institutions", [])
                for affiliation in [normalize_text(inst.get("author_affiliation"))]
                if affiliation
            }

            author_stats = authors[author_name]
            author_stats["occurrences"] += 1
            author_stats["affiliations"].update(affiliations)

            if not affiliations:
                author_stats["missing_occurrences"] += 1

            if len(author_stats["paper_examples"]) < 5:
                author_stats["paper_examples"].append(
                    {
                        "paper_id": paper_id,
                        "title": title,
                        "affiliations": sorted(affiliations),
                    }
                )

    inconsistent = {}
    for author_name, stats in authors.items():
        if len(stats["affiliations"]) > 1 or (
            stats["affiliations"] and stats["missing_occurrences"] > 0
        ):
            inconsistent[author_name] = {
                "occurrences": stats["occurrences"],
                "missing_occurrences": stats["missing_occurrences"],
                "affiliations": sorted(stats["affiliations"]),
                "paper_examples": stats["paper_examples"],
            }

    return authors, inconsistent


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Check whether the same author name appears with the same "
            "author_affiliation across all keywordSearch records."
        )
    )
    parser.add_argument("--product-type", default="ier")
    parser.add_argument(
        "--output-json",
        help="Optional path to save the inconsistent authors as JSON.",
    )
    args = parser.parse_args()

    records = fetch_all_records(args.product_type)
    authors, inconsistent = analyze_affiliations(records)

    print()
    print(f"Product type: {args.product_type}", flush=True)
    print(f"Records scanned: {len(records)}", flush=True)
    print(f"Distinct authors: {len(authors)}", flush=True)
    print(f"Authors with inconsistent affiliations: {len(inconsistent)}", flush=True)

    if inconsistent:
        print()
        print("Sample inconsistent authors:", flush=True)
        for index, (author_name, stats) in enumerate(sorted(inconsistent.items())[:20], start=1):
            print(f"{index}. {author_name}", flush=True)
            print(f"   affiliations: {stats['affiliations']}", flush=True)
            print(
                f"   occurrences: {stats['occurrences']}, "
                f"missing affiliation occurrences: {stats['missing_occurrences']}",
                flush=True,
            )

    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as handle:
            json.dump(inconsistent, handle, ensure_ascii=False, indent=2)
        print()
        print(f"Wrote details to {args.output_json}", flush=True)


if __name__ == "__main__":
    main()
