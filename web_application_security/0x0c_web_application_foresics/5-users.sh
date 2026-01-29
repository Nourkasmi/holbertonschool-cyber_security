#!/bin/bash
grep -oP "new user: name=\K\S+" auth.log | tr -d , | sort -u | paste -sd,
