# Coalition Server Tests

This directory contains test scripts for the Coalition Server functionality.

## Available Tests

### test_affinity_update.py

Tests the job affinity update functionality through the web interface API.

**Purpose:** 
Verifies that the `/json/updatejobs` endpoint correctly handles job affinity updates, which was previously broken due to parameter parsing issues.

**What it tests:**
1. Adding a job with initial affinity
2. Retrieving jobs from the server
3. Verifying initial affinity is set correctly  
4. Updating job affinity to a new value
5. Verifying the affinity was updated
6. Testing empty/blank affinity updates
7. Verifying empty affinity is handled correctly

**Usage:**
```bash
# Test against local server (localhost:19211)
python3 test/test_affinity_update.py

# Test against remote server
python3 test/test_affinity_update.py 10.230.8.90:19211
python3 test/test_affinity_update.py http://10.230.8.90:19211
```

**Expected Output:**
```
============================================================
COALITION SERVER AFFINITY UPDATE TEST
============================================================

1. Adding test job with initial affinity 'CPU'...
✓ Added job 'Affinity Test Job' with affinity 'CPU': 111

2. Retrieving jobs to find test job...
✓ Found test job with ID: 108

3. Verifying initial affinity is 'CPU'...
✓ Job 108 affinity verified: 'CPU'

4. Updating job affinity to 'GPU_HIGH'...
✓ Updated job 108 affinity to 'GPU_HIGH': 1

5. Verifying updated affinity is 'GPU_HIGH'...
✓ Job 108 affinity verified: 'GPU_HIGH'

6. Testing empty affinity update...
✓ Updated job 108 affinity to '': 1

7. Verifying empty affinity...
✓ Job 108 affinity verified: ''

============================================================
TEST RESULTS
============================================================
Passed: 7/7
Failed: 0/7
🎉 ALL TESTS PASSED - Affinity update functionality works correctly!
```

### test_worker_affinity_update.py

Tests the worker affinity update functionality through the web interface API.

**Purpose:** 
Verifies that the `/json/updateworkers` endpoint correctly handles worker affinity updates, which was previously broken due to parameter parsing issues.

**What it tests:**
1. Getting list of available workers
2. Finding a worker to test with
3. Updating worker affinity to a new value
4. Verifying the affinity was updated
5. Testing multiple affinity value changes
6. Testing empty/blank affinity updates
7. Restoring original affinity

**Usage:**
```bash
# Test against local server (localhost:19211)
python3 test/test_worker_affinity_update.py

# Test against remote server
python3 test/test_worker_affinity_update.py 10.230.8.90:19211
python3 test/test_worker_affinity_update.py http://10.230.8.90:19211
```

**Expected Output:**
```
============================================================
COALITION SERVER WORKER AFFINITY UPDATE TEST
============================================================

1. Getting list of available workers...
✓ Found worker 'coalition-ol9-1' with current affinity: 'rp'

2. Updating worker affinity to 'GPU_TEST'...
✓ Updated worker coalition-ol9-1 affinity to 'GPU_TEST': 1

3. Verifying updated affinity is 'GPU_TEST'...
✓ Worker coalition-ol9-1 affinity verified: 'GPU_TEST'

4. Updating worker affinity to 'CPU_PRIORITY'...
✓ Updated worker coalition-ol9-1 affinity to 'CPU_PRIORITY': 1

5. Verifying updated affinity is 'CPU_PRIORITY'...
✓ Worker coalition-ol9-1 affinity verified: 'CPU_PRIORITY'

6. Testing empty affinity update...
✓ Updated worker coalition-ol9-1 affinity to '': 1

7. Verifying empty affinity...
✓ Worker coalition-ol9-1 affinity verified: ''

8. Restoring original affinity 'rp'...
✓ Updated worker coalition-ol9-1 affinity to 'rp': 1

============================================================
TEST RESULTS
============================================================
Passed: 8/8
Failed: 0/8
🎉 ALL TESTS PASSED - Worker affinity update functionality works correctly!
```

### test_job_buttons.py

Tests all job button functionalities (Delete, Reset, Pause, etc.) through the web interface API.

**Purpose:** 
Verifies that job management buttons work correctly after fixing parameter parsing issues in endpoints like `/json/clearjobs`, `/json/resetjobs`, `/json/pausejobs`, etc.

**What it tests:**
1. Adding various test jobs
2. Reset Jobs functionality (`/json/resetjobs`)
3. Reset Error Jobs functionality (`/json/reseterrorjobs`)
4. Pause Jobs functionality (`/json/pausejobs`)
5. Start Jobs functionality (`/json/startjobs`)
6. Stop Jobs functionality (`/json/stopjobs`)
7. Multiple job operations at once
8. Clear Jobs (Delete) functionality (`/json/clearjobs`)
9. Verification that jobs were properly deleted

**Usage:**
```bash
# Test against local server (localhost:19211)
python3 test/test_job_buttons.py

# Test against remote server
python3 test/test_job_buttons.py 10.230.8.90:19211
python3 test/test_job_buttons.py http://10.230.8.90:19211
```

**Expected Output:**
```
============================================================
COALITION SERVER JOB BUTTONS TEST
============================================================

1. Adding test jobs...
✓ Added job 'Test Delete Job': 1
✓ Added job 'Test Reset Job': 2
✓ Added job 'Test Pause Job': 3
✓ Added job 'Test Error Job': 4
✓ Created test jobs: 1, 2, 3, 4

2. Testing Reset Jobs functionality...
✓ Reset Jobs successful: 1

3. Testing Reset Error Jobs functionality...
✓ Reset Error Jobs successful: 1

[... continuing for all button tests ...]

============================================================
TEST RESULTS
============================================================
Passed: 9/9
Failed: 0/9
🎉 ALL TESTS PASSED - Job button functionality works correctly!
```

### create_test_jobs.py

Creates various test jobs for manual testing of the server functionality.

**Usage:**
```bash
python3 test/create_test_jobs.py
```

## Running All Tests

To run all tests in sequence:

```bash
cd /path/to/coalition-server
python3 test/test_affinity_update.py
python3 test/test_worker_affinity_update.py
python3 test/test_job_buttons.py
python3 test/create_test_jobs.py
```

## Test Server Commands

For testing against the dedicated test server (opc@10.230.8.90):

```bash
# Run job affinity test on test server
ssh opc@10.230.8.90 "cd ~/coalition-server && python3 test/test_affinity_update.py"

# Run worker affinity test on test server  
ssh opc@10.230.8.90 "cd ~/coalition-server && python3 test/test_worker_affinity_update.py"

# Run job buttons test on test server
ssh opc@10.230.8.90 "cd ~/coalition-server && python3 test/test_job_buttons.py"

# Copy test files to test server
scp test/*.py opc@10.230.8.90:~/coalition-server/test/
```

## Adding New Tests

When creating new test scripts:

1. Follow the naming convention: `test_*.py`
2. Make scripts executable: `chmod +x test/test_*.py`
3. Include proper error handling and status reporting
4. Use the same server connection pattern as existing tests
5. Add documentation to this README
6. Handle the server's malformed JSON responses if needed (see `get_jobs()` in `test_affinity_update.py` for example)

## Common Issues

- **JSON Parsing Errors:** The server returns malformed JSON with trailing commas and single quotes. Use manual parsing or regex as shown in `test_affinity_update.py`
- **Server Not Running:** Make sure the Coalition Server is running on the expected port before running tests
- **Network Issues:** For remote testing, ensure SSH access and port connectivity