# Server Tests

This directory contains automated tests for the Coalition server.

The tests focus on **black-box behavior**: the server is started as an external
process and verified through real HTTP requests, without mocking internal
components.

---

## Test Scope

Currently, the tests cover:

- Server startup and shutdown
- Basic HTTP availability checks
- Endpoint reachability (protocol-level, not business logic)

These tests are intended to act as **regression tests** during refactoring and
modernization of the server codebase.

---

## Requirements

- Python 3.9+
- pytest
- requests

Install dependencies:

```bash
pip install pytest requests
