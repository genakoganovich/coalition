import requests
import pytest
from .conftest import BASE_URL


def test_json_root_returns_405(start_server):
    """
    /json is NOT a REST endpoint.
    A GET request to /json must return 405 Method Not Allowed.
    This behavior is intentional and must not be changed.
    """
    response = requests.get(BASE_URL + "json")

    assert response.status_code == 405, (
        f"/json returned {response.status_code}, expected 405 Method Not Allowed"
    )
