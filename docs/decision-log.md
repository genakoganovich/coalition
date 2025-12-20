# Decision Log

This document records key technical decisions made during the analysis,
testing, and refactoring of the legacy server.

The goal is to preserve *why* decisions were made, not the full discussion
or intermediate mistakes.

---

## 2025-12-19 — Testing-first refactoring strategy

### Context
The project contains a legacy Python web server (`server.py`, ~2400 LOC).
The server supports two execution modes:
- Windows Service (win32-specific)
- Simple server mode (used on Linux)

The refactoring and testing will be performed on Linux.

### Decisions
- Use a **test-first / characterization testing** approach before refactoring.
- Treat `main()` as the single entry point for the server on Linux.
- Ignore Windows Service–specific code during the initial testing and refactoring phase.

### Rationale
- Characterization tests allow safe refactoring without changing behavior.
- On Linux, the Windows Service code path is never executed.
- Reducing scope lowers the risk of accidental breakage.

### Consequences
- All initial tests will target the behavior of `main()`.
- Windows Service support may be revisited in a later phase if needed.

---

## 2025-12-19 — Testing strategy for Twisted-based server startup

### Context
The server uses Twisted and starts the global reactor inside `main()`.
The call to `reactor.run()` is blocking and never returns during normal operation.

### Decisions
- Do not unit-test `main()` directly.
- Use subprocess-based smoke and characterization tests to test server startup and behavior.
- Treat the server as a black box process during initial testing.

### Rationale
- Calling `reactor.run()` blocks the current process and cannot be stopped cleanly from a unit test.
- Subprocess-based tests reflect real production behavior.
- This approach allows safe testing without modifying legacy code.

### Consequences
- Tests will start and stop the server process externally.
- Initial tests will be slower but reliable.
---

---

## 2025-12-19 — First characterization test

### Context
Server port is defined in coalition.ini (`port=19211`).  
Main HTTP resource is `Root("public_html")`, subpaths `/xmlrpc`, `/json`, `/workers`.

### Decisions
- Use `/` endpoint on port 19211 as the first smoke test.
- Start the server in a subprocess to safely run tests without touching Twisted internals.
- Stop the server after test completion.

### Rationale
- reactor.run() blocks the process; cannot unit-test main() directly.
- Subprocess-based test simulates real usage and ensures server is responding.

### Consequences
- Tests may run slower due to subprocess startup.
- Future tests can cover `/xmlrpc`, `/json`, `/workers`.

---

## 2025-12-19 — Multi-endpoint smoke tests

### Context
The server exposes multiple HTTP endpoints: `/`, `/json`, `/xmlrpc`, `/workers`.

### Decisions
- Add a subprocess-based smoke test that validates availability of all core endpoints.
- Use active polling instead of fixed delays.

### Rationale
- Prevent regressions during refactoring.
- Ensure real server behavior is preserved.

### Consequences
- Server startup is validated before each endpoint test.
- Tests provide confidence for future architectural changes.
- 
### Endpoint behavior
The server is not REST-based.
Most endpoints (`/workers`, `/json`, `/xmlrpc`) do not support GET and correctly return HTTP 405.
HTTP 405 is treated as a valid response indicating endpoint presence.

### RPC protocol clarification
Endpoints `/json` and `/xmlrpc` both use XML-RPC.
Despite its name, `/json` does NOT implement JSON-RPC.
Sending JSON payloads results in XML deserialization errors.

### XML-RPC verification
Endpoint `/xmlrpc` correctly processes XML-RPC requests.
Invalid method names return faultCode 8001 ("procedure not found").
Infrastructure and XML parsing confirmed working.

### API reality check
The server does NOT implement real XML-RPC or JSON-RPC.
Despite inheriting from xmlrpc.XMLRPC, the `render()` method is overridden.
API is a custom HTTP RPC:
- routing is based on URL paths (e.g. /json/addjob)
- parameters are passed via query string (request.args)
- request body is not used

## 2025-12-19 — addjobbulknew error behavior

### Observation
Endpoint /json/addjobbulknew behaves inconsistently on invalid input:
- Logical validation errors return HTTP 200 with body "False"
- Invalid bulkSize type (non-integer) raises ValueError and results in HTTP 500

### Decision
Characterization tests explicitly document this behavior.
No normalization or error handling is added at this stage.

### Rationale
Tests must reflect real legacy behavior before refactoring.

## 2025-12-19 — XML-RPC error matrix

### Decision
Add characterization tests for /xmlrpc error behavior.

### Rationale
The server overrides xmlrpc.XMLRPC.render and does not follow standard XML-RPC.
Fault codes and HTTP status behavior must be documented before refactoring.

### Consequences
Tests assert presence of faults and HTTP status,
not compliance with XML-RPC specification.

## 2025-12-19 — Workers error matrix

### Decision
Characterization tests for /workers start/stop edge cases:
- Starting a worker twice
- Stopping a non-existent worker

### Rationale
Server legacy behavior may not forbid repeated start or stop.
Tests capture real behavior before refactoring.

### Consequences
HTTP responses (200/405) are documented.
Future refactoring can rely on these assertions.

# Decision Log

## 2025-12-20 — Job tree and bulk creation behavior

### Context
- Server stores jobs in `State.Jobs` as a dictionary of `Job` objects.  
- Root job has ID 0; all other jobs may reference a parent via `Parent` attribute.  
- Bulk jobs are created via `/json/addjobbulknew?parent=X&bulkSize=N`.  
- `/json/getjobs?id=X` traverses job children and parent hierarchy.

### Observation
- If `parent=0`, bulk jobs can still be created.  
- Bulk jobs receive unique IDs and append `--bulk_id=i` to `Command`.  
- If `parent` does not exist in `State.Jobs`, `addjobbulknew` returns `False`.  
- `getjobs` crashes with `KeyError` if a job’s `Parent` is `None`.  
- After server restart, `State.Jobs` contains only the root job (ID 0).  

### Decisions
- Document `addjobbulknew` behavior with valid and invalid parents.  
- Document `getjobs` behavior and its reliance on valid Parent links.  
- Characterization tests should cover:
  - Bulk creation with valid parent
  - Bulk creation with invalid parent
  - Retrieval via `/json/getjobs`
  - Behavior after server restart
  - Parent-child traversal and edge case `Parent=None`  

### Rationale
- Preserves legacy behavior in tests.  
- Ensures safe refactoring of job tree handling.  
- Highlights potential crash scenarios for future improvement.  

### Consequences
- Tests will assert current behavior without fixing crashes.  
- Bulk jobs’ `Command` field includes `--bulk_id=i` as expected.  
- Refactoring can later normalize `Parent=None` handling.  

---

## 2025-12-20 — Worker state verification

### Context
- Workers are listed via `/json/getworkers`.  
- Worker object fields: Name, Affinity, State, Finished, Error, LastJob, Load, FreeMemory, TotalMemory, Active.  
- Workers can be started and stopped manually or via server logic.

### Observation
- Worker shows `Active=true` when waiting, even with no jobs assigned.  
- Worker’s `Load` reflects CPU usage; `Finished` and `Error` counters track completed jobs.  
- Stopping a non-existent worker does not crash the server; returns HTTP 200.  
- Starting the same worker twice leaves state unchanged.

### Decisions
- Document legacy Worker behavior in characterization tests.  
- Capture worker edge cases:
  - Double start
  - Stop non-existent worker
  - Empty job queue
- Do not modify legacy Worker logic yet.

### Rationale
- Ensures tests reflect actual server behavior.  
- Allows future refactoring without breaking existing Worker handling.

### Consequences
- Tests verify Worker state fields and edge cases.  
- Server remains compatible with existing job scheduling logic.
