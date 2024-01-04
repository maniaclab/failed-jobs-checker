#!/bin/python3.6
from elasticsearch import Elasticsearch, exceptions as es_exceptions
from tabulate import tabulate
from datetime import datetime, timedelta
import subprocess
import os
import argparse

INDEX='jobs'
MAX_RESULTS=8192

def print_table(table):
    # Headers are the keys for the response dictionary
    try:
        header = table[0]["fields"].keys()
    except IndexError as e:
        print("No results for query!")
        return
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
    if len(rows) >= MAX_RESULTS:
        print("NOTE: There may be more results than presented here. Please consider tuning MAX_RESULTS in check2.py or reducing the query interval")

def time_now():
    current_date = datetime.now()
    return current_date.isoformat()

def hours_ago(N):
    now = datetime.now()
    then = now - timedelta(hours=N)
    return then.isoformat()

def query_builder(IDs):
    body = {
          "_source": "false", 
          "size": 1000,
          "fields": [
            {
              "field": "jobstatus"
            },
            {
              "field": "pandaid"
            },
            {
              "field": "piloterrorcode",
            },
            {
              "field": "modificationhost"
            }
          ],
          "query": {
            "bool": {
              "must": [],
              "must_not": []
            }
          }
        }
    post = {"should": []}
    for pandaid in IDs:
        match = { "match_phrase": { "pandaid": pandaid }}
        post["should"].append(match)
    body["query"]["bool"] = post
    return body

def get_failed_by_id(es_object, IDs=None):
    if not IDs:
        print("Getting local job IDs")
        IDs = get_local_job_ids()
    if IDs:
        body = query_builder(IDs)
        result = es_object.search(index=INDEX, body=body)
        table = result.body["hits"]["hits"]
        print_table(table)
    else:
        print("Could not get a list of job IDs. Try specifying on the commandline?")

def get_all_failed(es_object, startdate, enddate, computingsite):
    body={
      "_source": "false", 
      "size": MAX_RESULTS,
      "fields": [
        {
          "field": "pandaid"
        },
        {
          "field": "piloterrorcode",
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
    result = es_object.search(index=INDEX, body=body)
    table = result.body["hits"]["hits"]
    print_table(table)

def get_local_job_ids():
    # From Wenjing's script and dead-jobs.sh
    job_command = "grep -oh \"PandaID=..........\" $(condor_config_val EXECUTE)/dir_*/_condor_stdout | sort -u | cut -d'=' -f2"
    ret = subprocess.run(job_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ret.returncode != 0:
        raise Exception("Subprocess did not exit cleanly: %s" % ret.stderr)
    job_ids = ret.stdout.split()
    return job_ids
    
if __name__ == '__main__': 
    # Set up argument parsing
    parser = argparse.ArgumentParser(
                prog="FailedJobs",
                description="Query ATLAS Analytics Elasticsearch for failed jobs")
    parser.add_argument("mode", choices=["site","node"])
    parser.add_argument('-s', '--site', default="MWT2", help="Site, e.g. 'MWT2', 'AGLT2', 'SWT2_CPB', etc")
    parser.add_argument('-i', '--ids', nargs='+', help="space separated list of PanDA job IDs")
    parser.add_argument('-l', '--last', default=4, type=int, help="Maximum number of hours ago. Only relevant for 'site' mode")

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
    if args.mode == "site":
        get_all_failed(es, startdate, enddate, computingsite)
    elif args.mode == "node":
        IDs = args.ids
        get_failed_by_id(es, IDs)
