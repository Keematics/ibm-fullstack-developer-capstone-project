import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import os
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    # print("json data {} ".format(json_data))
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url,json_payload, **kwargs):
    # print(kwargs)
    print("POST from {} ".format(url))
    try:
        response = requests.post(url,params=kwargs,json=json_payload)
        print(response.text, "hello")
        return json.loads(response.text)
    except Exception as e:
        print(e)
        return

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list

def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result
        for dealer in dealers:
            dealer_doc = dealer["doc"]
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)
    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, **kwargs):
    results = []
    id = kwargs.get("id")
    if id:
        json_result = get_request(url, id=id)
    else:
        json_result = get_request(url)
   
    if json_result:
        print("PRINTING JSON RESULT >>> {} " .format(json_result))
        reviews = json_result["data"]["docs"]
        for review in reviews:
            dealer_review = review
            review_obj = DealerReview(dealership=dealer_review["dealership"],
                                   name=dealer_review["name"],
                                   purchase=dealer_review["purchase"],
                                   review=dealer_review["review"],
                                   purchase_date=dealer_review["purchase_date"],
                                   car_make=dealer_review["car_make"],
                                   car_model=dealer_review["car_model"],
                                   car_year=dealer_review["car_year"],
                                   id=dealer_review["dealership"]
                                   )
            sentiment = analyze_review_sentiments(review_obj.review)
            review_obj.sentiment = sentiment
            if "id" in dealer_review:
                review_obj.id = dealer_review["id"]
            if "purchase_date" in dealer_review:
                review_obj.purchase_date = dealer_review["purchase_date"]
            if "car_make" in dealer_review:
                review_obj.car_make = dealer_review["car_make"]
            if "car_model" in dealer_review:
                review_obj.car_model = dealer_review["car_model"]
            if "car_year" in dealer_review:
                review_obj.car_year = dealer_review["car_year"]
            
            # print(sentiment)
            results.append(review_obj)
    return results


def get_dealer_by_id_from_cf(url, id):
    json_result = get_request(url, id=id)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        for dealer in dealers:
            # print("PRINTING DEALER >>> {} " .format(dealer))
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                         id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                         short_name=dealer["short_name"],
                         st=dealer["st"], zip=dealer["zip"])
            results = dealer_obj
    return results
    

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    api_key = "jOajkLXDnTMjDMnlabjf2kFpemtDY4QgkaBjQgBnLRVK"
    url = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/4d445e70-8c94-48bf-b4ac-9ba830e56dc1"
    texttoanalyze= text
    version = '2022-03-30'
    authenticator = IAMAuthenticator(api_key) 
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2022-03-30',authenticator=authenticator) 
    natural_language_understanding.set_service_url(url) 
    response = natural_language_understanding.analyze( text=text ,features=Features(sentiment=SentimentOptions(targets=[text])), language='en').get_result() 
    label=json.dumps(response, indent=2) 
    label = response['sentiment']['document']['label'] 
    return(label) 