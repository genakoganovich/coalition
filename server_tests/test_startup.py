import subprocess
import requests
import time
import pytest
from .conftest import SERVER_CMD, BASE_URL, MAX_WAIT, POLL_INTERVAL


def test_server_startup():
    """
    Test that the server starts and responds to /json/getworkers endpoint.
    """
    server_proc = subprocess.Popen(SERVER_CMD)

    try:
        start_time = time.time()
        while True:
            try:
                response = requests.get(BASE_URL + "json/getworkers")
                if response.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass

            if time.time() - start_time > MAX_WAIT:
                raise TimeoutError(f"Server did not start within {MAX_WAIT} seconds")
            time.sleep(POLL_INTERVAL)

        assert response.status_code == 200

    finally:
        if server_proc.poll() is None:
            server_proc.terminate()
            server_proc.wait()
