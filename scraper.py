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
     language
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
     continent{
      continent
      countries {
       country
       fcv_status
       income_level
      }
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

def scrape_all(product_type):
    all_results = []
    size = 200
    start = 0

    data = search(product_type, start, size)
    total = data["total_count"]
    results = data["search_result"]
    all_results.extend(results)
    print(f"Total {product_type}: {total} records found")

    while len(all_results) < total:
        start += size
        data = search(product_type, start, size)
        results = data["search_result"]

        if not results:
            break
        all_results.extend(results)
        print(f"Fetched{len(all_results)}/{total}")

    return all_results

all_data = []
for p_type in ["ier", "srr", "egm"]:
    results = scrape_all(p_type)
    all_data.extend(results)
    print(f"{p_type}: {len(results)} records found")


# all_data = []
# for p_type in ["ier", "srr", "egm"]:
#     results = search(p_type, size = 300)
#     all_data.extend(results)
#     print(f"{p_type}: {len(results)} records found")

# Script is NOT resumable because records can be updated, and API does not support diff-based queries.

import os
if os.path.exists("data_output.json"):
    os.remove("data_output.json")

with open("data_output.json", "w") as f:
    json.dump(all_data, f, ensure_ascii= False, indent = 2)

print("Finished.")


# payload - fetch the variables
# """
# {"operationName":"KEYWORD_SEARCH",
# "variables":{"data":{"from":0,"keyword":"cash transfers",
# "size":"50","sort_by":"relevance","filters":{"product_type":[],
# "sector_name":[],"continents":[],"threeie_funded":[],
# "threeie_produced":[],"fcv_status":[],"countries":[],
# "equity_dimension":[],"primary_theme":[],"equity_focus":[],
# "year_of_publication":[],"dataset_available":[],
# "primary_dac_codes":[],"un_sdg":[],"primary_dataset_availability":[],
# "pre_registration":[],"interventions":[],"outcome":[],
# "evaluation_method":[],"confidence_level":[]}}},
# "query":"query KEYWORD_SEARCH($data: KeywordSearchInput!) 
# {\n  keywordSearch(data: $data) {\n    
# search_result {\n      product_type\n      title\n      synopsis\n      id\n      
# short_title\n      language\n      sector_name\n      journal\n      
# journal_volume\n      journal_issue\n      year_of_publication\n      
# publication_type\n      publication_url\n      grantholding_institution\n     
# evidence_programme\n      context\n      research_questions\n      
# main_finding\n      review_type\n      quantitative_method\n    
# qualitative_method\n      overall_of_studies\n      overall_of_high_quality_studies\n      
# overall_of_medium_quality_studies\n      headline_findings\n      pages\n      
# evaluation_design\n      authors {\n        author\n        institutions {\n          
# author_affiliation\n          department\n          author_country\n         
# __typename\n        }\n        __typename\n      }\n      continent {\n        
# continent\n        countries {\n          country\n          income_level\n          
# fcv_status\n          __typename\n        }\n        __typename\n      }\n      
# project_name {\n        project_name\n        implementation_agencies {\n          
# implementation_agency\n          implement_agency\n          __typename\n        }\n        
# funding_agencies {\n          program_funding_agency\n          agency_name\n         
# __typename\n        }\n        research_funding_agencies {\n          
# research_funding_agency\n          agency_name\n          __typename\n        }\n        __typename\n      }\n      
# publisher_location\n      status\n      threeie_funded\n      
# threeie_produced\n      is_bookmark\n      
# based_on_the_above_assessments_of_the_methods_how_would_you_rate_the_reliability_of_the_review\n      
# abstract\n      open_access\n      doi\n      equity_focus\n      equity_dimension\n      
# equity_description\n      keywords\n      evaluation_method\n      mixed_methods\n      
# unit_of_observation\n      methodology\n      main_findings\n      background\n      
# objectives\n      region\n      stateprovince_name\n      district_name\n      citytown_name\n      
# location_name\n      study_status\n      additional_url {\n        additional_url_address\n        
# additional_url\n        __typename\n      }\n      impact_evaluations\n      systematic_reviews\n      dataset_url\n      
# dataset_available\n      __typename\n    }\n    total_count\n    alternative_suggestions {\n      
# text\n      __typename\n    }\n    filters {\n      sector_wise_count {\n        buckets {\n          
# key\n          doc_count\n          by_secondary_sector {\n            buckets {\n              key\n              
# doc_count\n              __typename\n            }\n            __typename\n          }\n         
# __typename\n        }\n        __typename\n      }\n      continents_wise_count {\n        buckets {\n          
# key\n          doc_count\n          __typename\n        }\n        __typename\n      }\n     
# product_type_wise_count {\n        buckets {\n          key\n          doc_count\n         
# by_secondary_product {\n            buckets {\n              key\n              
# doc_count\n              __typename\n            }\n            __typename\n          }\n          
# __typename\n        }\n        __typename\n      }\n      threeie_funded_wise_count {\n        buckets {\n         
# key\n          doc_count\n          __typename\n        }\n        __typename\n      }\n      
# threeie_produced_wise_count {\n        buckets {\n          key\n          doc_count\n         
# __typename\n        }\n        __typename\n      }\n      fcv_wise_count {\n        buckets {\n         
# key\n          doc_count\n          __typename\n        }\n        __typename\n      }\n     
# countries_wise_count {\n        buckets {\n          key\n          doc_count\n          __typename\n        }\n      
# __typename\n      }\n      equity_focus_wise_count {\n        buckets {\n          key\n          
# doc_count\n          __typename\n        }\n        __typename\n      }\n      
# equity_dimension_wise_count {\n        buckets {\n          key\n          doc_count\n         
# __typename\n        }\n        __typename\n      }\n      year_of_publication_wise_count {\n       
# buckets {\n          key\n          doc_count\n          __typename\n        }\n        __typename\n      }\n    
# dataset_available_wise_count {\n        buckets {\n          key\n          doc_count\n          __typename\n        }\n     
# __typename\n      }\n      primary_dac_codes_wise_count {\n        buckets {\n          key\n          doc_count\n    
# __typename\n        }\n        __typename\n      }\n      un_sdg_wise_count {\n        buckets {\n          key\n    
# doc_count\n          __typename\n        }\n        __typename\n      }\n      
# primary_dataset_availability_wise_count {\n        buckets {\n          key\n        
# doc_count\n          __typename\n        }\n        __typename\n      }\n      pre_registration_wise_count {\n        
# buckets {\n          key\n          doc_count\n          __typename\n        }\n        __typename\n      }\n      
# interventions_wise_count {\n        buckets {\n          key\n          doc_count\n          __typename\n        }\n        
# __typename\n      }\n      outcome_wise_count {\n        buckets {\n          key\n          doc_count\n          
# __typename\n        }\n        __typename\n      }\n      evm_wise_count {\n        buckets {\n          key\n          
# doc_count\n          __typename\n        }\n        __typename\n      }\n      themes_wise_count {\n        
# by_primary_theme {\n          buckets {\n            key\n            doc_count\n            by_secondary_theme {\n              
# buckets {\n                key\n                doc_count\n                __typename\n              }\n              
# __typename\n            }\n            __typename\n          }\n          __typename\n        }\n        
# __typename\n      }\n      keywords_wise_count {\n        buckets {\n          key\n          doc_count\n          
# __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    selectedFilters {\n      primary_theme\n      
# sector_name\n      product_type\n      threeie_funded\n      threeie_produced\n      continents\n      countries\n      
# equity_focus\n      year_of_publication\n      equity_dimension\n      fcv_status\n      dataset_available\n      
# confidence_level\n      __typename\n    }\n    __typename\n  }\n}\n"}
# """
