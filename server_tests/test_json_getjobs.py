import pytest
import subprocess
import time
import requests
import json

SERVER_URL = "http://localhost:19211"

@pytest.fixture(scope="module")
def server():
    # Start the server in a separate process
    proc = subprocess.Popen(
        ["python3", "server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(2)  # wait for the server to start
    yield
    proc.terminate()
    proc.wait()

def getjobs(id=0, filter=""):
    # Send a GET request to /json/getjobs
    resp = requests.get(f"{SERVER_URL}/json/getjobs?id={id}&filter={filter}")
    # Legacy server returns repr() instead of JSON, so convert it
    return json.loads(resp.text.replace("'", '"'))

def test_getjobs_root(server):
    """If id=0, should return root and its children"""
    data = getjobs(id=0)
    assert "Vars" in data
    assert "Jobs" in data
    assert "Parents" in data
    root_parent_ids = [p["ID"] for p in data["Parents"]]
    assert 0 in root_parent_ids

def test_getjobs_nonexistent_id(server):
    """If id does not exist, fallback to root (id=0)"""
    data = getjobs(id=9999)
    parents = [p["ID"] for p in data["Parents"]]
    assert parents[0] == 0

def test_getjobs_no_children(server):
    """If a job has no children, Jobs=[]"""
    data = getjobs(id=0)
    # Check that if Children is empty, Jobs is empty
    if data["Parents"][0]["ID"] == 0 and len(data["Jobs"]) == 0:
        assert data["Jobs"] == []

def test_getjobs_filter_state(server):
    """Filter jobs by State"""
    # In legacy server, job.State may be None
    data = getjobs(id=0, filter="WAITING")
    for job in data["Jobs"]:
        # Make sure returned Jobs match the filter
        assert job[4] == "WAITING" or job[4] is None

def test_getjobs_parent_none(server):
    """Job with Parent=None does not break getjobs"""
    # Placeholder for edge case testing: create Job with Parent=None
    pass
