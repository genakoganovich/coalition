import requests
import pytest
from .conftest import BASE_URL

@pytest.mark.parametrize(
    "params, description",
    [
        ({"cmd": "echo hello"}, "missing title"),
        ({"title": "NoCmd"}, "missing cmd"),
        ({"title": "", "cmd": "echo"}, "empty title"),
        ({"title": "EmptyCmd", "cmd": ""}, "empty cmd"),
        ({}, "no parameters"),
    ],
)
def test_addjob_invalid_params(start_server, params, description):
    """
    Characterization test:
    Verify server behavior when /json/addjob is called
    with missing or invalid parameters.
    """
    response = requests.get(BASE_URL + "json/addjob", params=params)

    # Characterization: we only assert what IS, not what SHOULD be
    assert response.status_code == 200, (
        f"Unexpected HTTP status for case '{description}': {response.status_code}"
    )

    # Server should NOT return a valid job id
    # Usually it returns 0, -1, False, or an error string
    assert response.text.strip() != "", (
        f"Empty response for case '{description}'"
    )
