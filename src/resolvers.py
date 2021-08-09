import json
import requests
from loggerwrapper import Logger
import subprocess

logger = Logger("GraphQL resolver")
PROCESS_NAME = "resolvers"
GET = "get"
POST = "post"


def get_docker_host_ip():
    z = subprocess.check_output(['ip', '-4', 'route', 'list', 'match', '0/0'])
    z = z.decode()[len('default via ') :]
    return z[: z.find(' ')]

def build_http_request(type, method, data):

    # base_url = "http://172.17.0.1:5984"
    base_url = "http://host.docker.internal:5984"
    url = "{base_url}/{method}".format(base_url=base_url, method=method)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    authentication_header = ("admin", "admin")

    try:
        logger.info("{process_name}:build_http_request(): Sending {data} to {url}".format(
            process_name=PROCESS_NAME, data=data, url=url))

        if type == GET:
            r = requests.get(url=url, json=data, headers=headers,
                             auth=authentication_header, verify=False)
        else:
            r = requests.post(url=url, json=data, headers=headers,
                              auth=authentication_header, verify=False)

        r.raise_for_status()
    except Exception as e:
        logger.error("{process_name}:build_http_request(): The http request was not successful: {e}".format(
            process_name=PROCESS_NAME, e=e))
        raise
    return r


def resolve_indicator_by_id(_, info, id):
    try:
        id = int(id)
        logger.info("{process_name}:resolve_indicator_by_id(): Querying database for indicator {id}".format(
            process_name=PROCESS_NAME, id=id))

        #Connect to DBCOUCH and get indicators whose ID match the indicator ID
        method = "rivm2016/_find"
        request_json = {
            "selector": {
                "indicators": {
                    "$elemMatch": {
                        "id": id
                    }
                }
            }
        }
        response = build_http_request(POST, method, request_json)

        response_json = json.loads(response.content)

        logger.debug(json.dumps(response_json, indent=4))


        indicator = [indicator for doc in response_json["docs"]
                    for indicator in doc["indicators"] if indicator["id"] == id][0]
        
        logger.debug(json.dumps(indicator, indent=4))
        indicator.pop("value")

        return indicator
    except IndexError as e:
        logger.error("{process_name}:resolve_indicator_by_id(): No results found retrieving entry {id}".format(
            process_name=PROCESS_NAME, id=id))
        raise
    except Exception as e:
        logger.error("{process_name}:resolve_indicator_by_id(): Couldn't retrieve indicator {id}".format(
            process_name=PROCESS_NAME, id=id))
        raise



def resolve_indicators(_, info):
    logger.info("{process_name}:resolve_indicators: Obtaining all indicators".format(
        process_name=PROCESS_NAME))

    #Connect to DBCOUCH and get indicators whose ID match the indicator ID
    method = "rivm2016/_find"
    request_json = {
        "selector": {
            "indicators": {
                "$exists": True
            }
        }
    }
    response = build_http_request(POST, method, request_json)

    response_json = json.loads(response.content)

    indicators = [indicator for doc in response_json["docs"]
                  for indicator in doc["indicators"]]
    for indicator in indicators:
        indicator.pop("value")

    logger.info("{process_name}:resolve_indicators: Found {n} indicators".format(
        process_name=PROCESS_NAME, n=len(indicators)))

    for indicator in indicators:
        logger.debug(json.dumps(indicator, indent=4))

    return indicators


def resolve_entry_by_id(_, info, id):
    id = int(id)

    logger.info("{process_name}:resolve_entry_by_id(): Querying database for entry {id}".format(
        process_name=PROCESS_NAME, id=id))

    #Connect to DBCOUCH and get indicators whose ID match the indicator ID
    method = "rivm2016/_find"
    request_json = {
        "selector": {
            "entry": {
                "id": id
            }
        }
    }
    response = build_http_request(POST, method, request_json)

    response_json = json.loads(response.content)
    logger.debug(json.dumps(response_json, indent=4))
    try:
        entry = [doc["entry"] for doc in response_json["docs"] if doc["entry"]["id"] == id][0]
        entry["productName"] = entry["product_name"]
        entry.pop("product_name")

        logger.debug(json.dumps(entry, indent=4))

        return entry


    except IndexError as e:
        logger.error("{process_name}:resolve_entry_by_id(): No results found retrieving entry {id}".format(
            process_name=PROCESS_NAME, id=id))
        raise
    except Exception as e:
        logger.error("{process_name}:resolve_entry_by_id(): FFailed retrieving entry {id} because {e}".format(
            process_name=PROCESS_NAME, id=id, e=e))
        raise



def resolve_geography(*_):
    return {
        "shortName" : "NL",
        "name" : "Nederlands"
    }

def resolve_entries(_, info):
    logger.info("{process_name}:resolve_entries: Obtaining all indicators".format(
        process_name=PROCESS_NAME))

    #Connect to DBCOUCH and get indicators whose ID match the indicator ID
    method = "rivm2016/_find"
    request_json = {
        "selector": {
            "entry": {
                "$exists": True
            }
        }
    }
    response = build_http_request(POST, method, request_json)
    response_json = json.loads(response.content)

    entries = [doc["entry"] for doc in response_json["docs"]]
    logger.info("{process_name}:resolve_entries: Found {n} entries".format(
        process_name=PROCESS_NAME, n=len(entries)))

    for entry in entries:
        entry["productName"] = entry["product_name"]
        entry.pop("product_name")
        logger.debug(json.dumps(entry, indent=4))

    return entries

def resolve_impact(_,info,entryID, indicatorID):
    entryID = int(entryID)
    indicatorID = int(indicatorID)
    logger.info("{process_name}:resolve_impact(): Querying database for impact based on entry id {eid} and indicator id {iid}".format(
        process_name=PROCESS_NAME, eid=entryID, iid=indicatorID))

    #Connect to DBCOUCH and get indicators whose ID match the indicator ID
    method = "rivm2016/_find"
    request_json = {
    "selector": {
        "impacts": {
            "$elemMatch": {
                "entry_id": entryID,
                "indicator_id": indicatorID
            }
        }
    }
}
    response = build_http_request(POST, method, request_json)

    response_json = json.loads(response.content)
    logger.debug(json.dumps(response_json, indent=4))

    impact = {}
    try:
        impact = [impact for doc in response_json["docs"] for impact in doc["impacts"] if impact["indicator_id"] == indicatorID and impact["entry_id"] == entryID][0]
        impact["indicator"] = impact["indicator_id"]
        impact["entry"] = impact["entry_id"]
        impact.pop("entry_id")
        impact.pop("indicator_id")


        logger.debug(json.dumps(impact, indent=4))

        return impact
    except IndexError as e:
        logger.error("{process_name}:resolve_impact(): No results found retrieving impact".format(
            process_name=PROCESS_NAME))
        raise
    except Exception as e:
        logger.error("{process_name}:resolve_impact(): Failed retrieving impact because {e}".format(
            process_name=PROCESS_NAME, e=e))
        raise



def resolve_impact_related_to_entry(entry, info, indicatorID):
    logger.debug("{process_name}:resolve_impacts_related_to_entry(): Resolving impacts for entry {entry}".format(
        process_name=PROCESS_NAME, entry=entry["id"]))

    impact = resolve_impact(None, None, entry["id"], indicatorID)
    logger.debug("{process_name}:resolve_impacts_related_to_entry(): Retrieved impact {impact}".format(
        process_name=PROCESS_NAME, impact=json.dumps(impact, indent=4)))
    
    return impact

def resolve_indicator_for_impact(impact, info):
    logger.debug("{process_name}:resolve_indicator_for_impact(): Resolving indicator for impact {impact}".format(
        process_name=PROCESS_NAME, impact=impact["id"]))

    indicator = resolve_indicator_by_id(None, None,impact["indicator"])
    logger.debug("{process_name}:resolve_indicator_for_impact(): Retrieved indicator {indicator}".format(
        process_name=PROCESS_NAME, indicator=json.dumps(indicator, indent=4)))
    
    return indicator

def resolve_entry_for_impact(impact, info):
    logger.debug(info)
    logger.debug("{process_name}:resolve_indicator_for_impact(): Resolving indicator for impact {impact}".format(
        process_name=PROCESS_NAME, impact=impact["id"]))

    entry = resolve_entry_by_id(None, None, impact["entry"])
    logger.debug("{process_name}:resolve_indicator_for_impact(): Retrieved indicator {entry}".format(
        process_name=PROCESS_NAME, entry=json.dumps(entry, indent=4)))
    
    return entry
