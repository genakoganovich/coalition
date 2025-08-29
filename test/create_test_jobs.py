#!/usr/bin/env python3

import sys
import time
import http.client
import urllib.parse

# Server configuration
server_host = "localhost"
server_port = "19211"

def add_job(title, cmd, parent=0, expected_duration=None):
    """Add a job to the coalition server"""
    try:
        params = urllib.parse.urlencode({
            'parent': parent,
            'title': title,
            'cmd': cmd,
            'dir': '.',
            'priority': 1000,
            'retry': 10,
            'timeout': 0,
            'affinity': '',
            'dependencies': '',
            'localprogress': '',
            'globalprogress': ''
        })
        
        conn = http.client.HTTPConnection(f"{server_host}:{server_port}")
        conn.request("POST", "/json/addjob", params, {"Content-type": "application/x-www-form-urlencoded"})
        response = conn.getresponse()
        data = response.read()
        conn.close()
        
        print(f"Added job '{title}': {data.decode()}")
        return True
        
    except Exception as e:
        print(f"Error adding job '{title}': {e}")
        return False

def main():
    # Path to dummy work script (absolute path on remote server)
    dummy_script = "/home/opc/coalition-server/test/dummy_work.sh"
    
    # Create parent job
    print("Creating parent test job...")
    add_job("Test Job Parent", f"{dummy_script}", parent=0)
    
    # Get parent job ID (assuming it will be 1)
    parent_id = 1
    
    # Create 6 finished jobs (with dummy CPU work)
    print("Creating 6 CPU-intensive sub-jobs...")
    for i in range(1, 7):
        add_job(f"CPU Job {i}", f"{dummy_script} && echo 'CPU job {i} completed - loaded 1 core for 10 seconds'", parent=parent_id)
    
    # Create 3 working jobs (shorter dummy work)
    print("Creating 3 quick work sub-jobs...")
    for i in range(1, 4):
        add_job(f"Quick Job {i}", f"timeout 5s bash -c 'while true; do :; done' && echo 'Quick job {i} completed after 5 seconds'", parent=parent_id)
    
    # Create 1 waiting job
    print("Creating 1 waiting sub-job...")
    add_job("Waiting Job", f"{dummy_script} && echo 'Waiting job completed'", parent=parent_id)
    
    print("Test jobs with CPU load created successfully!")

if __name__ == "__main__":
    main()