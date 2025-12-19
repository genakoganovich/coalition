import subprocess
import time
import requests
import os
import signal

SERVER_CMD = ["python3", "server.py"]
SERVER_URL = "http://localhost:19211/"
STARTUP_TIMEOUT = 5  # секунд

def test_server_startup():
    server_proc = subprocess.Popen(SERVER_CMD)

    try:
        time.sleep(STARTUP_TIMEOUT)
        response = requests.get(SERVER_URL)
        assert response.status_code == 200
    finally:
        if server_proc.poll() is None:
            os.kill(server_proc.pid, signal.SIGINT)
            server_proc.wait()
