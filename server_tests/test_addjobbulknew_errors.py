import pytest
import requests
from .conftest import BASE_URL, start_server

# -------------------------------
# /json/addjobbulknew error cases
# -------------------------------
@pytest.mark.parametrize(
    "params, description",
    [
        ({"cmd": "echo hello", "bulkSize": "3"}, "missing title"),
        ({"title": "BulkJob", "bulkSize": "3"}, "missing cmd"),
        ({"title": "BulkJob", "cmd": "echo hello"}, "missing bulkSize"),
        ({"title": "BulkJob", "cmd": "echo hello", "bulkSize": "0"}, "bulkSize zero"),
        ({"title": "BulkJob", "cmd": "echo hello", "bulkSize": "-1"}, "bulkSize negative"),
        ({"title": "BulkJob", "cmd": "echo hello", "bulkSize": "abc"}, "bulkSize not a number"),
        ({}, "no parameters"),
    ]
)
def test_addjobbulknew_invalid_params(start_server, params, description):
    """
    Characterization test for /json/addjobbulknew invalid parameters.

    Legacy behavior:
    - numeric/zero/negative bulkSize or missing parameters => HTTP 200, body "False"
    - non-numeric bulkSize => HTTP 500
    """
    response = requests.get(BASE_URL + "json/addjobbulknew", params=params)

    if description == "bulkSize not a number":
        # Server crashes with 500 for non-numeric bulkSize
        assert response.status_code == 500, f"Expected 500 for {description}, got {response.status_code}"
    else:
        # Server returns "False" for missing or invalid numeric params
        assert response.status_code == 200, f"Unexpected HTTP status for {description}: {response.status_code}"
        assert response.text == "False", f"{description} returned unexpected body: {response.text}"
