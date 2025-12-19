import requests
import pytest
from .conftest import BASE_URL


# Only test real, accessible endpoints
ENDPOINTS = {
    "json/getworkers": {200},
    "json/getjobs?id=0": {200},
    "json/addjob?title=Ping&cmd=echo": {200},
}

def test_server_endpoints(start_server):
    """
    Test that accessible server endpoints respond with expected HTTP status codes.
    """
    for endpoint, allowed_codes in ENDPOINTS.items():
        response = requests.get(BASE_URL + endpoint)
        assert response.status_code in allowed_codes, (
            f"{endpoint} returned {response.status_code}, expected one of {allowed_codes}"
        )
