import subprocess
import requests
import os
import signal
import time

SERVER_CMD = ["python3", "server.py"]
SERVER_URL = "http://localhost:19211/"
MAX_WAIT = 10        # Maximum time to wait for server startup (seconds)
POLL_INTERVAL = 0.5  # Interval between availability checks (seconds)


def test_server_startup():
    """
    Verify that the server starts successfully and begins accepting HTTP connections.

    The test launches the server as a subprocess, actively waits until it responds
    on the configured HTTP port, and then shuts it down gracefully.
    """

    # Start the server in a separate process
    server_proc = subprocess.Popen(SERVER_CMD)

    try:
        # Actively wait until the server becomes available
        start_time = time.time()
        while True:
            try:
                response = requests.get(SERVER_URL)
                if response.status_code == 200:
                    break  # Server is up and responding
            except requests.exceptions.ConnectionError:
                pass  # Server not ready yet

            if time.time() - start_time > MAX_WAIT:
                raise TimeoutError(
                    f"Server did not start within {MAX_WAIT} seconds"
                )

            time.sleep(POLL_INTERVAL)

        # If we reached this point, the server started successfully
        assert response.status_code == 200

    finally:
        # Gracefully terminate the server process
        if server_proc.poll() is None:
            os.kill(server_proc.pid, signal.SIGINT)
            server_proc.wait()
