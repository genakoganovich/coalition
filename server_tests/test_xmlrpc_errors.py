def xmlrpc_call(method, params_xml=""):
    return f"""<?xml version="1.0"?>
<methodCall>
  <methodName>{method}</methodName>
  <params>
    {params_xml}
  </params>
</methodCall>
"""

import requests
from xml.etree import ElementTree as ET
from .conftest import BASE_URL

def parse_fault(xml_text):
    root = ET.fromstring(xml_text)
    fault = root.find("fault")
    assert fault is not None, "No <fault> element found"

    members = fault.findall(".//member")
    result = {}
    for m in members:
        name = m.find("name").text
        value = list(m.find("value"))[0].text
        result[name] = value
    return result


def test_xmlrpc_unknown_method_returns_fault(start_server):
    xml = """<?xml version="1.0"?>
<methodCall>
  <methodName>no_such_method</methodName>
  <params></params>
</methodCall>
"""
    r = requests.post(
        BASE_URL + "xmlrpc",
        data=xml,
        headers={"Content-Type": "text/xml"},
    )

    assert r.status_code == 200

    fault = parse_fault(r.text)
    assert fault["faultCode"] == "8001"
    assert "procedure" in fault["faultString"]
def test_xmlrpc_empty_method_name(start_server):
    xml = """<?xml version="1.0"?>
<methodCall>
  <methodName></methodName>
  <params></params>
</methodCall>
"""
    r = requests.post(
        BASE_URL + "xmlrpc",
        data=xml,
        headers={"Content-Type": "text/xml"},
    )

    assert r.status_code == 200

    fault = parse_fault(r.text)
    # просто фиксируем, не угадываем
    assert "faultCode" in fault
    assert "faultString" in fault
def test_xmlrpc_invalid_xml(start_server):
    xml = "<methodCall><broken>"

    r = requests.post(
        BASE_URL + "xmlrpc",
        data=xml,
        headers={"Content-Type": "text/xml"},
    )

    assert r.status_code in {200, 500}
def test_xmlrpc_non_xml_payload(start_server):
    r = requests.post(
        BASE_URL + "xmlrpc",
        data="hello world",
        headers={"Content-Type": "text/plain"},
    )

    assert r.status_code in {200, 500}
