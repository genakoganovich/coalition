#!/bin/bash

# Dummy work script - loads 1 CPU core for 10 seconds
# This script simulates CPU-intensive work for testing purposes

echo "Starting dummy work - loading 1 CPU core for 10 seconds..."
echo "Start time: $(date)"

# Create a CPU-intensive loop for 10 seconds
timeout 10s bash -c 'while true; do :; done' &
WORK_PID=$!

# Wait for the work to complete
wait $WORK_PID

echo "Dummy work completed at: $(date)"
echo "Total duration: 10 seconds"