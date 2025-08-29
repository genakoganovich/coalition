#!/bin/bash
cd /opt/coalition/logs
find . -name "*" -mtime +2 -exec rm -f {} \;
