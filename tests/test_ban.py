""" Test for ban endpoint """
# pylint: disable=redefined-outer-name,no-member,unused-argument,unused-import

import json
from unittest.mock import patch, Mock
import azure.functions as func
from ban import main, ban_map
from tests import mocks
from tests.fixtures import mock_env_access_key, mock_env_no_access_key, CLIENT_HEADERS

def test_ban_function_access_error(mock_env_no_access_key):
    """ ban access error """
    print("*** test_ban_function_access_error")

    # Construct a mock HTTP request.
    req = func.HttpRequest(
        method='GET',
        body=json.dumps({
            'BAN': '123456'
        }),
        url='/api/ban')

    # Call the function.
    resp = main(req)
    resp_json = json.loads(resp.get_body())
    print(resp_json)

    # Check the output.
    assert resp_json['status'] == 'error'

def test_ban_missing_param(mock_env_access_key):
    """ ban missing ban param"""
    print("*** test_ban_missing_param")

    # Construct a mock HTTP request.
    req = func.HttpRequest(
        method='GET',
        headers=CLIENT_HEADERS,
        body=json.dumps({}).encode('utf8'),
        url='/api/ban')

    # Call the function.
    resp = main(req)
    resp_json = json.loads(resp.get_body())
    print(f"resp_json: {resp_json}")

    # Check the output.
    assert resp_json['status'] == 'error'

def test_ban_empty_get(mock_env_access_key):
    """ ban missing ban param"""
    print("*** test_ban_missing_param")

    # Construct a mock HTTP request.
    req = func.HttpRequest(
        method='GET',
        headers=CLIENT_HEADERS,
        body=None,
        url='/api/ban')

    # Call the function.
    resp = main(req)
    resp_json = json.loads(resp.get_body())
    print(f"resp_json: {resp_json}")

    # Check the output.
    assert resp.status_code == 200

@patch('requests.get')
def test_ban_success(mock_get, mock_env_access_key):
    """ ban happy path"""
    print("*** test_ban_success")

    mock_get.return_value.json.return_value=mocks.SOCRATA_RESPONSE

    # Construct a mock HTTP request.
    req = func.HttpRequest(
        method='GET',
        headers=CLIENT_HEADERS,
        body=json.dumps({
            'BAN': '123456'
        }).encode('utf8'),
        url='/api/ban')

    # Call the function.
    resp = main(req)
    resp_json = json.loads(resp.get_body())
    print(f"resp_json: {resp_json}")

    # Check the output.
    assert isinstance(resp_json, list)
    assert len(resp_json) == 2
    one_resp = resp_json[0]
    for prop in ban_map:
        assert prop in one_resp
