#!/usr/bin/env python3

import sys
import time
import http.client
import urllib.parse
import json
import re

# Server configuration
server_host = "localhost"
server_port = "19211"

def make_request(method, path, params=None):
    """Make HTTP request to coalition server"""
    try:
        conn = http.client.HTTPConnection(f"{server_host}:{server_port}")
        
        if method == "GET":
            if params:
                path += "?" + urllib.parse.urlencode(params)
            conn.request(method, path)
        else:
            body = urllib.parse.urlencode(params) if params else ""
            headers = {"Content-type": "application/x-www-form-urlencoded"}
            conn.request(method, path, body, headers)
        
        response = conn.getresponse()
        data = response.read()
        conn.close()
        
        return response.status, data.decode()
        
    except Exception as e:
        print(f"Error making request to {path}: {e}")
        return None, str(e)

def add_job(title, cmd, priority=1000, affinity=""):
    """Add a job to the coalition server"""
    params = {
        'parent': 0,
        'title': title,
        'cmd': cmd,
        'dir': '.',
        'priority': priority,
        'retry': 1,
        'timeout': 0,
        'affinity': affinity,
        'dependencies': '',
        'localprogress': '',
        'globalprogress': ''
    }
    
    status, response = make_request("POST", "/json/addjob", params)
    if status == 200:
        print(f"✓ Added job '{title}': {response}")
        return int(response) if response.isdigit() else None
    else:
        print(f"✗ Failed to add job '{title}': {response}")
        return None

def get_jobs():
    """Get all jobs from the server"""
    status, response = make_request("GET", "/json/getjobs")
    if status == 200:
        try:
            # Fix malformed JSON with trailing commas and single quotes
            fixed_response = response.replace(",]", "]").replace(",}", "}")
            fixed_response = fixed_response.replace("'", '"')
            jobs_data = json.loads(fixed_response)
            
            # Convert job arrays to dictionaries
            jobs_raw = jobs_data.get('Jobs', [])
            vars_list = jobs_data.get('Vars', [])
            
            jobs = []
            for job_array in jobs_raw:
                job_dict = {}
                for i, var_name in enumerate(vars_list):
                    if i < len(job_array):
                        job_dict[var_name] = job_array[i]
                jobs.append(job_dict)
            
            return jobs
        except json.JSONDecodeError as e:
            print(f"✗ Failed to parse jobs response: {e}")
            return []
    else:
        print(f"✗ Failed to get jobs: {response}")
        return []

def test_job_button_endpoint(endpoint, job_ids, operation_name):
    """Test a job button endpoint with multiple job IDs"""
    # Format the request like the web interface does
    params = []
    for job_id in job_ids:
        params.append(('id', str(job_id)))
    
    query_string = "&".join([f"{k}={v}" for k, v in params])
    path = f"/json/{endpoint}?" + query_string
    
    print(f"Testing {operation_name}: {path}")
    
    status, response = make_request("GET", path.split("?")[0], dict(params))
    
    if status == 200:
        print(f"✓ {operation_name} successful: {response}")
        return response == "1"  # Server returns "1" for success
    else:
        print(f"✗ {operation_name} failed: status={status}, response={response}")
        return False

def test_job_buttons():
    """Test all job button functionalities"""
    print("=" * 60)
    print("COALITION SERVER JOB BUTTONS TEST")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    print(f"\n1. Adding test jobs...")
    
    # Add test jobs
    job1_id = add_job("Test Delete Job", "echo 'test delete'")
    job2_id = add_job("Test Reset Job", "echo 'test reset'") 
    job3_id = add_job("Test Pause Job", "echo 'test pause'")
    job4_id = add_job("Test Error Job", "false")  # Command that will fail
    
    if not all([job1_id, job2_id, job3_id, job4_id]):
        print("✗ Failed to create test jobs")
        return False
        
    print(f"✓ Created test jobs: {job1_id}, {job2_id}, {job3_id}, {job4_id}")
    success_count += 1
    total_tests += 1
    
    # Wait for jobs to be processed
    time.sleep(2)
    
    print(f"\n2. Testing Reset Jobs functionality...")
    if test_job_button_endpoint("resetjobs", [job2_id], "Reset Jobs"):
        success_count += 1
    total_tests += 1
    
    print(f"\n3. Testing Reset Error Jobs functionality...")
    if test_job_button_endpoint("reseterrorjobs", [job4_id], "Reset Error Jobs"):
        success_count += 1
    total_tests += 1
    
    print(f"\n4. Testing Pause Jobs functionality...")
    if test_job_button_endpoint("pausejobs", [job3_id], "Pause Jobs"):
        success_count += 1
    total_tests += 1
    
    print(f"\n5. Testing Start Jobs functionality...")
    if test_job_button_endpoint("startjobs", [job3_id], "Start Jobs"):
        success_count += 1
    total_tests += 1
    
    print(f"\n6. Testing Stop Jobs functionality...")  
    if test_job_button_endpoint("stopjobs", [job3_id], "Stop Jobs"):
        success_count += 1
    total_tests += 1
    
    print(f"\n7. Testing multiple job operations...")
    if test_job_button_endpoint("resetjobs", [job1_id, job2_id], "Reset Multiple Jobs"):
        success_count += 1
    total_tests += 1
    
    print(f"\n8. Testing Clear Jobs (Delete) functionality...")
    if test_job_button_endpoint("clearjobs", [job1_id, job2_id, job3_id, job4_id], "Clear Jobs"):
        success_count += 1
    total_tests += 1
    
    print(f"\n9. Verifying jobs were deleted...")
    jobs_after = get_jobs()
    remaining_test_jobs = [job for job in jobs_after if 'Test' in job.get('Title', '')]
    
    if len(remaining_test_jobs) == 0:
        print("✓ All test jobs successfully deleted")
        success_count += 1
    else:
        print(f"✗ {len(remaining_test_jobs)} test jobs still remain")
    total_tests += 1
    
    # Print results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {success_count}/{total_tests}")
    print(f"Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - Job button functionality works correctly!")
        return True
    else:
        print("❌ SOME TESTS FAILED - Job button functionality has issues!")
        return False

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        global server_host, server_port
        server_url = sys.argv[1]
        if "://" in server_url:
            server_url = server_url.split("://")[1]
        if ":" in server_url:
            server_host, server_port = server_url.split(":")
        else:
            server_host = server_url
    
    print(f"Testing Coalition Server at {server_host}:{server_port}")
    
    # Run the test
    test_success = test_job_buttons()
    
    # Exit with appropriate code
    sys.exit(0 if test_success else 1)

if __name__ == "__main__":
    main()