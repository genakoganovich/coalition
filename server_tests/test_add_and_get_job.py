import requests
import pytest
from .conftest import BASE_URL, wait_for_job


def test_add_and_get_job(start_server):
    """
    Test adding a job via /json/addjob and verifying it appears in /json/getjobs.

    Steps:
    1. Add a job via /json/addjob.
    2. Wait until the job appears in /json/getjobs.
    3. Verify the job ID is present in server response.
    """
    # Step 1: Add a job
    params = {"title": "TestJob", "cmd": "echo hello"}
    response = requests.get(BASE_URL + "json/addjob", params=params)
    assert response.status_code == 200, "Failed to add job"

    job_id = int(response.text)
    assert job_id > 0, f"Invalid job ID returned: {job_id}"

    # Step 2: Wait until the job appears
    wait_for_job(job_id)

    # Step 3: Verify job is present
    resp = requests.get(BASE_URL + "json/getjobs?id=0")
    assert str(job_id) in resp.text, "Added job not found in server response"
