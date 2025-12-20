import pytest
import requests
from .conftest import BASE_URL, start_server

# -------------------------------
# /json/addjob error codes mapping
# -------------------------------

# Mapping of description -> server-returned error code for addjob
ADDJOB_ERROR_CODES = {
    "missing title": "8",
    "missing cmd": "9",
    "empty title": "10",
    "empty cmd": "11",
    "no parameters": "12",
}

@pytest.mark.parametrize(
    "params, description",
    [
        ({"cmd": "echo hello"}, "missing title"),
        ({"title": "TestJob"}, "missing cmd"),
        ({"title": "" , "cmd": "echo hello"}, "empty title"),
        ({"title": "TestJob", "cmd": ""}, "empty cmd"),
        ({}, "no parameters"),
    ]
)
def test_addjob_invalid_params(start_server, params, description):
    """Characterization test for /json/addjob invalid parameters."""
    response = requests.get(BASE_URL + "json/addjob", params=params)
    # Legacy behavior: always returns 200
    assert response.status_code == 200, f"{description} returned {response.status_code}"
    assert response.text == ADDJOB_ERROR_CODES[description], (
        f"{description} returned unexpected body: {response.text}"
    )


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
    """Characterization test for /json/addjobbulknew invalid parameters."""
    response = requests.get(BASE_URL + "json/addjobbulknew", params=params)

    # Legacy behavior:
    # - numeric/zero/negative bulkSize returns "False" with 200
    # - non-numeric bulkSize crashes with 500
    if description == "bulkSize not a number":
        assert response.status_code == 500, f"Expected 500 for {description}, got {response.status_code}"
    else:
        assert response.status_code == 200, f"Unexpected HTTP status for {description}: {response.status_code}"
        assert response.text in ["False"], f"{description} returned unexpected body: {response.text}"
