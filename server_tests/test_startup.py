import subprocess
import requests
import os
import signal
import time

SERVER_CMD = ["python3", "server.py"]
SERVER_URL = "http://localhost:19211/"
MAX_WAIT = 10  # максимальное время ожидания старта сервера, сек
POLL_INTERVAL = 0.5  # интервал опроса сервера, сек

def test_server_startup():
    # Запуск сервера в отдельном процессе
    server_proc = subprocess.Popen(SERVER_CMD)

    try:
        # Активное ожидание: проверяем, что сервер отвечает
        start_time = time.time()
        while True:
            try:
                response = requests.get(SERVER_URL)
                if response.status_code == 200:
                    break  # сервер поднялся успешно
            except requests.exceptions.ConnectionError:
                pass  # сервер ещё не готов
            if time.time() - start_time > MAX_WAIT:
                raise TimeoutError(f"Server did not start within {MAX_WAIT} seconds")
            time.sleep(POLL_INTERVAL)

        # Если дошли сюда, сервер поднялся → тест пройден
        assert response.status_code == 200

    finally:
        # Корректное завершение процесса сервера
        if server_proc.poll() is None:
            os.kill(server_proc.pid, signal.SIGINT)
            server_proc.wait()
