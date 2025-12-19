import requests
import pytest
from .conftest import BASE_URL

def test_worker_start_twice(start_server):
    """
    Characterization test:
    Attempt to start the same worker twice.
    Expect server to respond with legacy behavior.
    """
    # 1️⃣ Первый запуск
    r1 = requests.get(BASE_URL + "json/startworker")
    assert r1.status_code in {200, 405}

    # 2️⃣ Второй запуск
    r2 = requests.get(BASE_URL + "json/startworker")
    # фиксируем поведение
    assert r2.status_code in {200, 405}  # legacy может вернуть 405
    print(f"Start twice: first={r1.status_code}, second={r2.status_code}")


def test_worker_stop_missing(start_server):
    """
    Characterization test:
    Attempt to stop a worker when none is running.
    Expect server to respond with legacy behavior.
    """
    r = requests.get(BASE_URL + "json/stopworker")
    # legacy может вернуть 200 или 405
    assert r.status_code in {200, 405}
    print(f"Stop missing worker: status={r.status_code}")
