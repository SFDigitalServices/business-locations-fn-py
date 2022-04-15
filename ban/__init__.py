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

# map socrata fieldnames to existing ban lookup fieldnames
ban_map = {
    "ban": "BAN",
    "owners": "OWNERS",
    "businessname": "BusinessName",
    "dbaname": "DBAName",
    "streetaddress": "StreetAddress",
    "city": "City",
    "state": "State",
    "postalcd": "PostalCd",
    "lin": "LIN",
    "busstartdate": "BusstartDate",
    "locstartdate": "2019-08-14T00:00:00.000",
    "mailingaddress": "580 4TH ST",
    "mailcitystatezip": "SAN FRANCISCO CA 94107-",
    "locationnumber": "226",
    "orgtype": "C-Corp"
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

        else:
            response = common.get_http_response_by_status(200)

        headers = {
            "Access-Control-Allow-Origin": "*"
        }
        return common.func_json_response(response, headers, "message")

    #pylint: disable=broad-except
    except Exception as err:
        logging.error("Status HTTP error occurred: %s", traceback.format_exc())
        msg_error = f"This endpoint encountered an error. {err}"
        func_response = json.dumps(jsend.error(msg_error))
        return func.HttpResponse(func_response, status_code=500)