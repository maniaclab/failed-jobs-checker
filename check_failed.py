#!/bin/python3.6
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from tabulate import tabulate
from datetime import datetime, timedelta
import os
import argparse

MAX_RESULTS=4096

def print_table(table):
    # Headers are the keys for the response dictionary
    header = table[0]["fields"].keys()
    # Each match to the query returns a dictionary of fields. The value of each
    # field is wrapped in a list which only has a length of 1 for our data.  So
    # we take the first (and only) field from each list to flatten the data
    # into a row.
    rows=[]
    for x in table:
        row = []
        for key in x["fields"].keys():
            if key == "pandaid":
                url = "https://bigpanda.cern.ch/job?pandaid=" + str(x["fields"][key][0])
                row.append(url)
            else:
                row.append(x["fields"][key][0])
        rows.append(row)
    # Then print using the field keys as a header and the list of rows as values
    print(tabulate(rows, header))

def time_now():
    current_date = datetime.now()
    return current_date.isoformat()

def hours_ago(N):
    now = datetime.now()
    then = now - timedelta(hours=N)
    return then.isoformat()
    
if __name__ == '__main__': 
    # Set up argument parsing
    parser = argparse.ArgumentParser(
                prog="FailedJobs",
                description="Query ATLAS Analytics Elasticsearch for failed jobs")
    parser.add_argument('-s', '--site', default="MWT2")
    parser.add_argument('-l', '--last', default=24, type=int)

    args = parser.parse_args()
    # Get the computing site, default to MWT2
    computingsite = args.site
    # Calculate a start and end date based on the time range asked for
    startdate = hours_ago(args.last)
    enddate = time_now()
            
    host = os.getenv('ES_HOST', 'atlas-kibana.mwt2.org')
    port = int(os.getenv('ES_PORT', '9200'))
    user = os.getenv('ES_USER')
    pwd  = os.getenv('ES_PASS')
    if user == None or pwd == None:
        raise Exception("ES_USER and ES_PASS must both be defined")
    es = Elasticsearch(
            hosts=[{'host': host, 'port': port, 'scheme': 'https'}],
            basic_auth=(user, pwd),
            request_timeout=60)
    index = 'jobs'
    
    body={
      "_source": "false", 
      "size": MAX_RESULTS,
      "fields": [
        {
          "field": "pandaid"
        },
        {
          "field": "piloterrorcode"
        },
        {
          "field": "modificationhost"
        },
        {
          "field": "batchid"
        }
      ],
      "query": {
        "bool": {
          "must": [
            {
              "match_phrase": {
                "jobstatus": "failed"
              }
            }
          ],
          "should": [],
          "must_not": [],
          "filter": [
            {
              "bool": {
                "should": [
                  {
                    "term": {
                      "computingsite": {
                        "value": computingsite
                      }
                    }
                  }
                ]
              }
            },
            {
              "range": {
                "modificationtime": {
                  "format": "strict_date_optional_time",
                  "gte": startdate,
                  "lte": enddate
                }
              }
            }
          ]
        }
      }
    } 
    result = es.search(index=index, body=body)
    table = result.body["hits"]["hits"]
    print_table(table)
