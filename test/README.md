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
python3 test/create_test_jobs.py
```

## Test Server Commands

For testing against the dedicated test server (opc@10.230.8.90):

```bash
# Run affinity test on test server
ssh opc@10.230.8.90 "cd ~/coalition-server && python3 test/test_affinity_update.py"

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