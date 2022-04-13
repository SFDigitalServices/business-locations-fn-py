""" Test for status/http endpoint """
import json
from unittest.mock import patch
import azure.functions as func
from status_http import main

def test_status_http_function():
    """ test_status_http_function """
    # Construct a mock HTTP request.
    req = func.HttpRequest(
        method='GET',
        body=None,
        url='/api/status/http')

    # Call the function.
    resp = main(req)
    # print response body
    print(resp.get_body())
    # loads response body as json
    resp_json = json.loads(resp.get_body())

    # Check the output.
    assert resp_json['status'] == 'success'


def test_status_http_function_other():
    """ test_status_http_function_other """
    # Construct a mock HTTP request.
    req = func.HttpRequest(
        method='POST',
        body="TEST",
        url='/api/status/http')

    # Call the function.
    resp = main(req)

    assert resp.status_code == 202

def test_status_http_function_request_error():
    """ test_status_http_function error """

    with patch('status_http.func_json_response') as mock:
        mock.side_effect = ValueError('ERROR_TEST')
        # Construct a mock HTTP request.
        req = func.HttpRequest(
            method='GET',
            body=None,
            url='/api/status/http')

        # Call the function.
        resp = main(req)

        resp_json = json.loads(resp.get_body())
        print(resp_json)
        # Check the output.
        assert resp_json['status'] == 'error'
