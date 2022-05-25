""" ban init file """
import os
import json
import logging
import traceback
import requests
import jsend
from dateutil import parser
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
    "busenddate": "BusEndDate",
    "locstartdate": "LocstartDate",
    "locenddate": "LocEndDate",
    "mailingaddress": "MailingAddress",
    "mailcitystatezip": "MailCityStateZip",
    "locationnumber": "LocationNumber",
    "orgtype": "OrgType"
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
                    'Authorization': 'Basic ' + os.getenv('BAN_API_AUTH_API_KEY'),
                    'X-App-Token': os.getenv('BAN_API_APP_TOKEN')
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

                for field, value in result.items():
                    if field in ban_map:
                        field = ban_map.get(field)

                    # date formatting MM-DD-YYYY
                    if value and field.lower().endswith('date'):
                        the_date = parser.parse(value)
                        value = the_date.strftime('%m-%d-%Y')

                    mapped_result[field] = value

                # add missing items
                # socrata will not return fields which have null values
                for field in ban_map.values():
                    if field not in mapped_result:
                        mapped_result[field] = ""

                mapped_results.append(mapped_result)

            return func.HttpResponse(
                json.dumps(mapped_results),
                status_code=200,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "*"
                }
            )

        response = common.get_http_response_by_status(200)
        return common.func_json_response(
            response,
            {"Access-Control-Allow-Origin": "*"},
            "message"
        )

    #pylint: disable=broad-except
    except Exception as err:
        logging.error("Status HTTP error occurred: %s", traceback.format_exc())
        msg_error = f"This endpoint encountered an error. {err}"
        func_response = json.dumps(jsend.error(msg_error))
        return func.HttpResponse(func_response, status_code=500)
