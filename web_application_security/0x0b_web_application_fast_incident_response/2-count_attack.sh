#!/bin/bash
attacker=$(awk '{print $1}' $1 | sort | uniq -c | sort -nr | head -n 1 | awk '{print $2}')
awk -v ip=$attacker '$1 == ip {count++} END {print count}' $1
