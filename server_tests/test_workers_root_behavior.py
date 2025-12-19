import requests
import pytest
from .conftest import BASE_URL


def test_workers_root_returns_405(start_server):
    """
    /workers is not a REST endpoint.
    GET request must return 405 Method Not Allowed.
    This behavior is intentional and must be preserved.
    """
    response = requests.get(BASE_URL + "workers")

    assert response.status_code == 405, (
        f"/workers returned {response.status_code}, expected 405 Method Not Allowed"
    )
