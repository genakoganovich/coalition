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
    # Create parent job
    print("Creating parent test job...")
    add_job("Test Job Parent", "echo 'Parent job completed'", parent=0)
    
    # Get parent job ID (assuming it will be 1)
    parent_id = 1
    
    # Create 6 finished jobs (4 minute duration)
    print("Creating 6 finished sub-jobs...")
    for i in range(1, 7):
        add_job(f"Finished Job {i}", f"sleep 240 && echo 'Finished job {i} completed after 4 minutes'", parent=parent_id)
    
    # Create 3 working jobs (20 second duration)
    print("Creating 3 working sub-jobs...")
    for i in range(1, 4):
        add_job(f"Working Job {i}", f"sleep 20 && echo 'Working job {i} completed after 20 seconds'", parent=parent_id)
    
    # Create 1 waiting job
    print("Creating 1 waiting sub-job...")
    add_job("Waiting Job", "echo 'Waiting job - ready to execute'", parent=parent_id)
    
    print("Test jobs created successfully!")

if __name__ == "__main__":
    main()