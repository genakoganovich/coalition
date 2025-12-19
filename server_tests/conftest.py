import subprocess
import requests
import time
import pytest

SERVER_CMD = ["python3", "server.py"]
BASE_URL = "http://localhost:19211/"
MAX_WAIT = 15  # seconds
POLL_INTERVAL = 0.5  # seconds

@pytest.fixture(scope="module")
def start_server():
    """Launch the server in a separate process and ensure it's ready."""
    server_proc = subprocess.Popen(SERVER_CMD)
    try:
        start_time = time.time()
        while True:
            try:
                resp = requests.get(BASE_URL + "json/getworkers")
                if resp.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
            if time.time() - start_time > MAX_WAIT:
                raise TimeoutError("Server did not start within {} seconds".format(MAX_WAIT))
            time.sleep(POLL_INTERVAL)
        yield server_proc
    finally:
        if server_proc.poll() is None:
            server_proc.terminate()
            server_proc.wait()


def wait_for_job(job_id, timeout=MAX_WAIT):
    """Actively wait until a job with the given ID appears in /json/getjobs."""
    start_time = time.time()
    while True:
        resp = requests.get(BASE_URL + f"json/getjobs?id=0")
        if resp.status_code != 200:
            raise RuntimeError("Failed to fetch jobs from server")

        # Search for the job ID in response text (server returns repr)
        if str(job_id) in resp.text:
            return
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Job {job_id} did not appear within {timeout} seconds")
        time.sleep(POLL_INTERVAL)
