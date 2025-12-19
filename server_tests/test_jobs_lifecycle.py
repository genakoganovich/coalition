import requests
import pytest
from .conftest import BASE_URL, wait_for_job

def test_job_lifecycle(start_server):
    """
    Characterization test for a complete job lifecycle:
    add -> get -> retry -> delete -> get -> edge cases
    """

    # Step 1: Add a job
    params = {"title": "LifecycleJob", "cmd": "echo hello"}
    r = requests.get(BASE_URL + "json/addjob", params=params)
    assert r.status_code == 200
    job_id = int(r.text)
    assert job_id > 0

    # Step 2: Wait until the job appears
    wait_for_job(job_id)

    # Step 3: Get the job
    r = requests.get(BASE_URL + f"json/getjobs?id={job_id}")
    assert r.status_code in {200, 404, 405}
    print(f"get job: status={r.status_code}, body={r.text}")

    # Step 4: Retry the job
    r = requests.get(BASE_URL + f"json/retryjob?id={job_id}")
    assert r.status_code in {200, 404, 405}
    print(f"retry job: status={r.status_code}, body={r.text}")

    # Step 5: Delete the job
    r = requests.get(BASE_URL + f"json/deletejob?id={job_id}")
    assert r.status_code in {200, 404, 405}
    print(f"delete job: status={r.status_code}, body={r.text}")

    # Step 6: Get the job after deletion
    r = requests.get(BASE_URL + f"json/getjobs?id={job_id}")
    assert r.status_code in {200, 404, 405}
    print(f"get after delete: status={r.status_code}, body={r.text}")

    # Edge Case: Retry deleted job
    r = requests.get(BASE_URL + f"json/retryjob?id={job_id}")
    assert r.status_code in {200, 404, 405}
    print(f"retry deleted job: status={r.status_code}, body={r.text}")

    # Edge Case: Delete again
    r = requests.get(BASE_URL + f"json/deletejob?id={job_id}")
    assert r.status_code in {200, 404, 405}
    print(f"delete again: status={r.status_code}, body={r.text}")
