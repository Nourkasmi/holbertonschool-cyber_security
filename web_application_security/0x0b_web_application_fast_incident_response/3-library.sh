#!/bin/bash
awk -v ip="54.145.34.34" '$1 == ip {print $12}' "logs.txt" | sort | uniq -c | sort -nr | head -n 1 | awk '{print $2}' | tr -d '"'