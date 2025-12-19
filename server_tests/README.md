# server_tests

This folder contains automated tests for the Coalition server.

## Tests included

1. **test_startup.py**  
   Checks that the server starts and responds to HTTP requests.

2. **test_endpoints.py**  
   Ensures key endpoints return valid HTTP codes.

3. **test_add_and_get_job.py**  
   Tests adding a job via `/json/addjob` and retrieving it via `/json/getjobs`.

## How to run tests

```bash
pytest server_tests/ -v
