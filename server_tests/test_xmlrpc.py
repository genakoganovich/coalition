import requests
import pytest
from .conftest import BASE_URL


XMLRPC_PING = """<?xml version="1.0"?>
<methodCall>
  <methodName>ping</methodName>
  <params></params>
</methodCall>
"""


def test_xmlrpc_unknown_method_returns_fault(start_server):
    """
    /xmlrpc processes XML-RPC requests.
    Unknown method names must return faultCode 8001.
    """
    response = requests.post(
        BASE_URL + "xmlrpc",
        data=XMLRPC_PING,
        headers={"Content-Type": "text/xml"},
    )

    assert response.status_code == 200
    assert "<fault>" in response.text
    assert "<int>8001</int>" in response.text
    assert "procedure ping not found" in response.text
