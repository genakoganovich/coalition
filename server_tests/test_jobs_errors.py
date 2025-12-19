import requests
import pytest
from .conftest import BASE_URL

@pytest.mark.parametrize(
    "params, description",
    [
        ({"title": "Job1", "cmd": "echo"}, "valid job"),
        ({"cmd": "echo"}, "missing title"),
        ({"title": "Job2"}, "missing cmd"),
        ({"title": "", "cmd": "echo"}, "empty title"),
        ({"title": "Job3", "cmd": ""}, "empty cmd"),
        ({}, "no parameters"),
    ],
)
def test_addjob_invalid_params(start_server, params, description):
    """Characterization: /json/addjob with invalid/missing params"""
    r = requests.get(BASE_URL + "json/addjob", params=params)
    assert r.status_code in {200, 500, 405}, (
        f"{description}: unexpected status {r.status_code}"
    )
    print(f"{description}: status={r.status_code}, body={r.text}")


@pytest.mark.parametrize(
    "params, description",
    [
        ({"title": "BulkJob", "cmd": "echo hello", "bulkSize": "0"}, "bulkSize zero"),
        ({"title": "BulkJob", "cmd": "echo hello", "bulkSize": "-1"}, "bulkSize negative"),
        ({"title": "BulkJob", "cmd": "echo hello", "bulkSize": "abc"}, "bulkSize not a number"),
        ({}, "no parameters"),
    ],
)
def test_addjobbulknew_invalid_params(start_server, params, description):
    """Characterization: /json/addjobbulknew with invalid/missing params"""
    r = requests.get(BASE_URL + "json/addjobbulknew", params=params)
    assert r.status_code in {200, 500, 405}, (
        f"{description}: unexpected status {r.status_code}"
    )
    print(f"{description}: status={r.status_code}, body={r.text}")


def test_getjob_unknown_id(start_server):
    """Request /json/getjobs with unknown ID"""
    r = requests.get(BASE_URL + "json/getjobs?id=99999")
    assert r.status_code in {200, 404, 405}
    print(f"get unknown job ID: status={r.status_code}, body={r.text}")


def test_deletejob_unknown_id(start_server):
    """Attempt to delete non-existent job"""
    r = requests.get(BASE_URL + "json/deletejob?id=99999")
    assert r.status_code in {200, 404, 405}
    print(f"delete unknown job ID: status={r.status_code}, body={r.text}")


def test_retryjob_unknown_id(start_server):
    """Attempt to retry job with invalid ID"""
    r = requests.get(BASE_URL + "json/retryjob?id=99999")
    assert r.status_code in {200, 404, 405}
    print(f"retry unknown job ID: status={r.status_code}, body={r.text}")
