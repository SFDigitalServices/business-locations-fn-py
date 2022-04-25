""" ban init file """
import os
import json
import logging
import traceback
import requests
import jsend
import azure.functions as func
from requests.models import Response
from shared_code import common

# map existing ban lookup fieldnames to socrata fieldnames
ban_map = {
    "BAN": "ban",
    "OWNERS": "owners",
    "BusinessName": "businessname",
    "DBAName": "dbaname",
    "StreetAddress": "streetaddress",
    "City": "city",
    "State": "state",
    "PostalCd": "postalcd",
    "LIN": "lin",
    "BusstartDate": "busstartdate",
    "BusEndDate": "busenddate",
    "LocstartDate": "locstartdate",
    "LocEndDate": "locenddate",
    "MailingAddress": "mailingaddress",
    "MailCityStateZip": "mailcitystatezip",
    "LocationNumber": "locationnumber",
    "OrgType": "orgtype"
}

headers = {
    "Access-Control-Allow-Origin": "*"
}

def main(req: func.HttpRequest) -> func.HttpResponse:
    """ main function for ban """
    logging.info('Status processed a request.')

    try:
        common.validate_access(req)

        response = Response()
        if req.get_body() and len(req.get_body()):
            response = common.get_http_response_by_status(202)

            req_json = req.get_json()
            print(f"ban req_json: {req_json}")

            params = {}
            if "BAN" not in req_json:
                raise ValueError("Missing BAN parameter")

            # query socrata
            params["BAN"] = req_json.get("BAN")
            response = requests.get(
                os.getenv('BAN_API_URL'),
                headers={
                    'Authorization': 'Basic ' + os.getenv('ADDRESS_SVC_AUTH_API_KEY'),
                    'X-App-Token': os.getenv('ADDRESS_SVC_APP_TOKEN')
                },
                params=params
            )

            print(f"response: {response}")
            response.raise_for_status()

            # map field names for each result
            resp_json = response.json()
            print(f"resp_json: {resp_json}")
            mapped_results = []
            for result in resp_json:
                mapped_result = {}
                for ban_field, socrata_field in ban_map.items():
                    mapped_result[ban_field] = result.get(socrata_field, "")
                mapped_results.append(mapped_result)

            return func.HttpResponse(
                json.dumps(mapped_results),
                status_code=200,
                mimetype="application/json",
                headers=headers
            )

        response = common.get_http_response_by_status(200)
        return common.func_json_response(response, headers, "message")

    #pylint: disable=broad-except
    except Exception as err:
        logging.error("Status HTTP error occurred: %s", traceback.format_exc())
        msg_error = f"This endpoint encountered an error. {err}"
        func_response = json.dumps(jsend.error(msg_error))
        return func.HttpResponse(func_response, status_code=500)
