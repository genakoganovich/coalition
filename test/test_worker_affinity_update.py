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

def get_workers():
    """Get all workers from the server"""
    status, response = make_request("GET", "/json/getworkers")
    if status == 200:
        try:
            # Fix malformed JSON with trailing commas and single quotes  
            fixed_response = response.replace(",]", "]").replace(",}", "}")
            fixed_response = fixed_response.replace("'", '"')
            fixed_response = fixed_response.replace("true", "true").replace("false", "false")
            fixed_response = fixed_response.replace(",\n]", "]").strip()
            
            workers_data = json.loads(fixed_response)
            
            # Convert worker arrays to dictionaries
            workers_raw = workers_data.get('Workers', [])
            vars_list = workers_data.get('Vars', [])
            
            workers = []
            for worker_array in workers_raw:
                worker_dict = {}
                for i, var_name in enumerate(vars_list):
                    if i < len(worker_array):
                        worker_dict[var_name] = worker_array[i]
                workers.append(worker_dict)
            
            return workers
            
        except Exception as e:
            print(f"✗ Failed to parse workers response: {e}")
            print(f"Response: {response[:200]}...")
            return []
    else:
        print(f"✗ Failed to get workers: {response}")
        return []

def update_worker_affinity(worker_id, new_affinity):
    """Update worker affinity using the web interface endpoint"""
    params = {
        'id': worker_id,
        'prop': 'Affinity',
        'value': new_affinity
    }
    
    status, response = make_request("GET", "/json/updateworkers", params)
    
    if status == 200:
        print(f"✓ Updated worker {worker_id} affinity to '{new_affinity}': {response}")
        return True
    else:
        print(f"✗ Failed to update worker {worker_id} affinity: status={status}, response={response}")
        return False

def find_worker_by_name(workers, worker_name):
    """Find worker by Name in workers list"""
    for worker in workers:
        if worker.get('Name') == worker_name:
            return worker
    return None

def verify_worker_affinity(worker_name, expected_affinity):
    """Verify that a worker has the expected affinity"""
    workers = get_workers()
    worker = find_worker_by_name(workers, worker_name)
    
    if worker:
        actual_affinity = worker.get('Affinity', '')
        if actual_affinity == expected_affinity:
            print(f"✓ Worker {worker_name} affinity verified: '{actual_affinity}'")
            return True
        else:
            print(f"✗ Worker {worker_name} affinity mismatch: expected '{expected_affinity}', got '{actual_affinity}'")
            return False
    else:
        print(f"✗ Worker {worker_name} not found")
        return False

def test_worker_affinity_update():
    """Test the worker affinity update functionality"""
    print("=" * 60)
    print("COALITION SERVER WORKER AFFINITY UPDATE TEST")
    print("=" * 60)
    
    success_count = 0
    total_tests = 0
    
    print(f"\n1. Getting list of available workers...")
    workers = get_workers()
    
    if not workers:
        print("✗ No workers found - cannot test worker affinity updates")
        print("Please ensure at least one worker is connected to the server")
        return False
    
    # Use the first worker for testing
    test_worker = workers[0]
    worker_name = test_worker.get('Name')
    original_affinity = test_worker.get('Affinity', '')
    
    print(f"✓ Found worker '{worker_name}' with current affinity: '{original_affinity}'")
    success_count += 1
    total_tests += 1
    
    # Test parameters
    test_affinity = "GPU_TEST"
    test_affinity_2 = "CPU_PRIORITY"
    
    print(f"\n2. Updating worker affinity to '{test_affinity}'...")
    if update_worker_affinity(worker_name, test_affinity):
        success_count += 1
    total_tests += 1
    
    # Wait for update to take effect
    time.sleep(1)
    
    print(f"\n3. Verifying updated affinity is '{test_affinity}'...")
    if verify_worker_affinity(worker_name, test_affinity):
        success_count += 1
    total_tests += 1
    
    print(f"\n4. Updating worker affinity to '{test_affinity_2}'...")
    if update_worker_affinity(worker_name, test_affinity_2):
        success_count += 1
    total_tests += 1
    
    # Wait for update to take effect
    time.sleep(1)
    
    print(f"\n5. Verifying updated affinity is '{test_affinity_2}'...")
    if verify_worker_affinity(worker_name, test_affinity_2):
        success_count += 1
    total_tests += 1
    
    print(f"\n6. Testing empty affinity update...")
    if update_worker_affinity(worker_name, ""):
        success_count += 1
    total_tests += 1
    
    # Wait for update to take effect
    time.sleep(1)
    
    print(f"\n7. Verifying empty affinity...")
    if verify_worker_affinity(worker_name, ""):
        success_count += 1
    total_tests += 1
    
    # Restore original affinity
    print(f"\n8. Restoring original affinity '{original_affinity}'...")
    if update_worker_affinity(worker_name, original_affinity):
        success_count += 1
    total_tests += 1
    
    # Print results
    print("\n" + "=" * 60)
    print("TEST RESULTS")
    print("=" * 60)
    print(f"Passed: {success_count}/{total_tests}")
    print(f"Failed: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED - Worker affinity update functionality works correctly!")
        return True
    else:
        print("❌ SOME TESTS FAILED - Worker affinity update functionality has issues!")
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
    test_success = test_worker_affinity_update()
    
    # Exit with appropriate code
    sys.exit(0 if test_success else 1)

if __name__ == "__main__":
    main()