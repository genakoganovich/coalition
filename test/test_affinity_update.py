#!/usr/bin/env python3

import sys
import time
import http.client
import urllib.parse
import json

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

def add_job(title, cmd, affinity=""):
    """Add a job to the coalition server"""
    params = {
        'parent': 0,
        'title': title,
        'cmd': cmd,
        'dir': '.',
        'priority': 1000,
        'retry': 1,
        'timeout': 0,
        'affinity': affinity,
        'dependencies': '',
        'localprogress': '',
        'globalprogress': ''
    }
    
    status, response = make_request("POST", "/json/addjob", params)
    if status == 200:
        print(f"✓ Added job '{title}' with affinity '{affinity}': {response}")
        return True
    else:
        print(f"✗ Failed to add job '{title}': {response}")
        return False

def get_jobs():
    """Get all jobs from the server"""
    status, response = make_request("GET", "/json/getjobs")
    if status == 200:
        try:
            # Parse the malformed JSON manually
            import re
            
            # Extract the Vars array
            vars_match = re.search(r'"Vars":\[(.*?)\]', response)
            if not vars_match:
                print("✗ Could not find Vars in response")
                return []
            
            vars_str = vars_match.group(1)
            vars_list = [v.strip().strip("'\"") for v in vars_str.split(',')]
            
            # Extract job arrays
            jobs_match = re.search(r'"Jobs":\[(.*?)\], "Parents"', response, re.DOTALL)
            if not jobs_match:
                print("✗ Could not find Jobs in response")
                return []
            
            jobs_str = jobs_match.group(1).strip()
            if not jobs_str:
                return []
            
            # Split job arrays manually
            job_arrays = []
            current_array = []
            in_array = False
            bracket_count = 0
            current_item = ""
            
            for char in jobs_str:
                if char == '[':
                    bracket_count += 1
                    in_array = True
                    current_item += char
                elif char == ']':
                    bracket_count -= 1
                    current_item += char
                    if bracket_count == 0:
                        # Parse this job array
                        array_content = current_item.strip('[]')
                        job_values = []
                        for item in array_content.split(','):
                            item = item.strip()
                            if item.startswith('"') and item.endswith('"'):
                                job_values.append(item.strip('"'))
                            elif item == 'null':
                                job_values.append(None)
                            elif item.replace('.', '').replace('-', '').isdigit():
                                if '.' in item:
                                    job_values.append(float(item))
                                else:
                                    job_values.append(int(item))
                            else:
                                job_values.append(item.strip('"\''))
                        job_arrays.append(job_values)
                        current_item = ""
                        in_array = False
                elif in_array:
                    current_item += char
            
            # Convert to dictionaries
            jobs = []
            for job_array in job_arrays:
                job_dict = {}
                for i, var_name in enumerate(vars_list):
                    if i < len(job_array):
                        job_dict[var_name] = job_array[i]
                jobs.append(job_dict)
            
            return jobs
            
        except Exception as e:
            print(f"✗ Failed to parse jobs response: {e}")
            print(f"Response: {response[:200]}...")
            return []
    else:
        print(f"✗ Failed to get jobs: {response}")
        return []

def update_job_affinity(job_id, new_affinity):
    """Update job affinity using the web interface endpoint"""
    params = {
        'id': job_id,
        'prop': 'Affinity', 
        'value': new_affinity
    }
    
    status, response = make_request("GET", "/json/updatejobs", params)
    
    if status == 200:
        print(f"✓ Updated job {job_id} affinity to '{new_affinity}': {response}")
        return True
    else:
        print(f"✗ Failed to update job {job_id} affinity: status={status}, response={response}")
        return False

def find_job_by_title(jobs, title):
    """Find job by title in jobs list - return the most recent one"""
    matching_jobs = []
    for job in jobs:
        if job.get('Title') == title:
            matching_jobs.append(job)
    
    if not matching_jobs:
        return None
    
    # Return the job with the highest ID (most recent)
    return max(matching_jobs, key=lambda job: job.get('ID', 0))

def verify_job_affinity(job_id, expected_affinity):
    """Verify that a job has the expected affinity"""
    jobs = get_jobs()
    for job in jobs:
        if job.get('ID') == job_id:
            actual_affinity = job.get('Affinity', '')
            if actual_affinity == expected_affinity:
                print(f"✓ Job {job_id} affinity verified: '{actual_affinity}'")
                return True
            else:
                print(f"✗ Job {job_id} affinity mismatch: expected '{expected_affinity}', got '{actual_affinity}'")
                return False
    
    print(f"✗ Job {job_id} not found")
    return False

def test_affinity_update():
    """Test the affinity update functionality"""
    print("=" * 60)
    print("COALITION SERVER AFFINITY UPDATE TEST")
    print("=" * 60)
    
    # Test parameters
    test_job_title = "Affinity Test Job"
    test_command = "echo 'Testing affinity update functionality'"
    initial_affinity = "CPU"
    updated_affinity = "GPU_HIGH"
    
    success_count = 0
    total_tests = 6
    
    print(f"\n1. Adding test job with initial affinity '{initial_affinity}'...")
    if add_job(test_job_title, test_command, initial_affinity):
        success_count += 1
    
    # Wait for job to be added
    time.sleep(1)
    
    print(f"\n2. Retrieving jobs to find test job...")
    jobs = get_jobs()
    test_job = find_job_by_title(jobs, test_job_title)
    
    if test_job:
        job_id = test_job.get('ID')
        print(f"✓ Found test job with ID: {job_id}")
        success_count += 1
    else:
        print(f"✗ Test job '{test_job_title}' not found")
        return False
    
    print(f"\n3. Verifying initial affinity is '{initial_affinity}'...")
    if verify_job_affinity(job_id, initial_affinity):
        success_count += 1
    
    print(f"\n4. Updating job affinity to '{updated_affinity}'...")
    if update_job_affinity(job_id, updated_affinity):
        success_count += 1
    
    # Wait for update to take effect
    time.sleep(1)
    
    print(f"\n5. Verifying updated affinity is '{updated_affinity}'...")
    if verify_job_affinity(job_id, updated_affinity):
        success_count += 1
    
    print(f"\n6. Testing empty affinity update...")
    if update_job_affinity(job_id, ""):
        success_count += 1
    
    # Wait for update to take effect
    time.sleep(1)
    
    print(f"\n7. Verifying empty affinity...")
    if verify_job_affinity(job_id, ""):
        success_count += 1
        total_tests += 1  # This was an extra test
    
    # Print results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {success_count}/{total_tests}")
    print(f"Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - Affinity update functionality works correctly!")
        return True
    else:
        print("❌ SOME TESTS FAILED - Affinity update functionality has issues!")
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
    test_success = test_affinity_update()
    
    # Exit with appropriate code
    sys.exit(0 if test_success else 1)

if __name__ == "__main__":
    main()