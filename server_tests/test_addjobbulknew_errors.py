import requests
import pytest
from .conftest import BASE_URL

@pytest.mark.parametrize(
    "params, description, expected_status",
    [
        ({"cmd": "echo hello", "bulkSize": "3"}, "missing title", 200),
        ({"title": "BulkJob", "bulkSize": "3"}, "missing cmd", 200),
        ({"title": "BulkJob", "cmd": "echo hello"}, "missing bulkSize", 200),
        ({"title": "BulkJob", "cmd": "echo hello", "bulkSize": "0"}, "bulkSize zero", 200),
        ({"title": "BulkJob", "cmd": "echo hello", "bulkSize": "-1"}, "bulkSize negative", 200),
        ({"title": "BulkJob", "cmd": "echo hello", "bulkSize": "abc"}, "bulkSize not a number", 500),
        ({}, "no parameters", 200),
    ],
)
def test_addjobbulknew_invalid_params(start_server, params, description, expected_status):
    """
    Characterization test:
    Document actual server behavior for invalid /json/addjobbulknew calls.
    """
    response = requests.get(BASE_URL + "json/addjobbulknew", params=params)

    assert response.status_code == expected_status, (
        f"{description}: expected HTTP {expected_status}, got {response.status_code}"
    )

    if expected_status == 200:
        assert response.text.strip() in {"False", "0"}, (
            f"{description}: unexpected response body {response.text!r}"
        )
