import requests
import json

# Fetch API from website INSPECT
API_URL = "https://api.developmentevidence.3ieimpact.org/graphql"

def search(product_type, start = 0, size = 200):
    query = """
    query ($data: KeywordSearchInput!){
     keywordSearch(data: $data){
     total_count
     search_result{
     id
     product_type
     title
     year_of_publication
     sector_name
     abstract
     evaluation_design
     evaluation_method

    authors {
      author
      institutions {
        author_affiliation
        department
        author_country
      }
    }
    
     continent{
      continent
      countries { country }
      }
     }
     }
    }
    """

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
                "threeie_produced": []
            }
        }
    }

    response = requests.post(API_URL, json = {"query": query, "variables": variables})
    return response.json()["data"]["keywordSearch"]

print(search("ier",30, 1))

query = """
query RECORD_DETAIL($id: Int!) {
  recordDetail(id: $id) {
  
    project_name {
      project_name
      funding_agencies {
        agency_name
        program_funding_agency
      }
      research_funding_agencies {
        agency_name
        research_funding_agency
      }
    }

    research_funding_agency {
      agency_name
      research_funding_agency
    }
  }
}
"""

variables = {"id": 38383}

response = requests.post(
    API_URL,
    json={
        "query": query,
        "variables": variables
    }
)

data = response.json()
record = data["data"]["recordDetail"]
print(record)