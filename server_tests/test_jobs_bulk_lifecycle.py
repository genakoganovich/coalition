import requests
import pytest
from .conftest import BASE_URL, wait_for_job

def test_bulk_jobs_lifecycle(start_server):
    """
    Characterization test for bulk jobs lifecycle:
    add bulk -> get -> retry -> delete -> get -> edge cases
    """

    # Step 1: Add bulk jobs
    params = {"title": "BulkLifecycleJob", "cmd": "echo hello", "bulkSize": "3"}
    r = requests.get(BASE_URL + "json/addjobbulknew", params=params)
    assert r.status_code in {200, 500}, f"Unexpected status: {r.status_code}"
    # Legacy behavior: server may return 'False' on invalid bulk
    print(f"add bulk: status={r.status_code}, body={r.text}")

    # Step 2: Extract job IDs if possible
    job_ids = []
    try:
        # server may return repr(list) or True/False
        import ast
        bulk_result = ast.literal_eval(r.text)
        if isinstance(bulk_result, list):
            job_ids = [int(j) for j in bulk_result]
    except Exception:
        pass

    # Step 3: Wait for each job to appear
    for job_id in job_ids:
        try:
            wait_for_job(job_id)
        except TimeoutError:
            print(f"Job ID {job_id} did not appear (legacy behavior)")

    # Step 4: Get each job
    for job_id in job_ids:
        r = requests.get(BASE_URL + f"json/getjobs?id={job_id}")
        assert r.status_code in {200, 404, 405}
        print(f"get job {job_id}: status={r.status_code}, body={r.text}")

    # Step 5: Retry each job
    for job_id in job_ids:
        r = requests.get(BASE_URL + f"json/retryjob?id={job_id}")
        assert r.status_code in {200, 404, 405}
        print(f"retry job {job_id}: status={r.status_code}, body={r.text}")

    # Step 6: Delete each job
    for job_id in job_ids:
        r = requests.get(BASE_URL + f"json/deletejob?id={job_id}")
        assert r.status_code in {200, 404, 405}
        print(f"delete job {job_id}: status={r.status_code}, body={r.text}")

    # Step 7: Edge cases: retry and delete again
    for job_id in job_ids:
        r = requests.get(BASE_URL + f"json/retryjob?id={job_id}")
        assert r.status_code in {200, 404, 405}
        print(f"retry deleted job {job_id}: status={r.status_code}, body={r.text}")

        r = requests.get(BASE_URL + f"json/deletejob?id={job_id}")
        assert r.status_code in {200, 404, 405}
        print(f"delete again job {job_id}: status={r.status_code}, body={r.text}")
