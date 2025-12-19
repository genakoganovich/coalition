import subprocess
import requests
import os
import signal
import time

SERVER_CMD = ["python3", "server.py"]
BASE_URL = "http://localhost:19211"

ENDPOINTS = {
    "/": {200},
    "/workers": {200, 400, 405},
    "/json": {200, 400, 405},
    "/xmlrpc": {200, 400, 405},
}

MAX_WAIT = 10
POLL_INTERVAL = 0.5


def wait_for_server():
    start_time = time.time()
    while True:
        try:
            r = requests.get(BASE_URL + "/")
            if r.status_code == 200:
                return
        except requests.exceptions.ConnectionError:
            pass

        if time.time() - start_time > MAX_WAIT:
            raise TimeoutError("Server did not start")

        time.sleep(POLL_INTERVAL)


def test_server_endpoints():
    server_proc = subprocess.Popen(SERVER_CMD)

    try:
        wait_for_server()

        for endpoint, allowed_codes in ENDPOINTS.items():
            response = requests.get(BASE_URL + endpoint)
            assert response.status_code in allowed_codes, (
                f"{endpoint} returned {response.status_code}, "
                f"expected one of {allowed_codes}"
            )

    finally:
        if server_proc.poll() is None:
            os.kill(server_proc.pid, signal.SIGINT)
            server_proc.wait()
