#!/bin/bash
tail -n 1000 auth.log | grep -oP "USER=\K\S+" | uniq -c | awk '{print $2}'
