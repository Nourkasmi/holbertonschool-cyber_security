#!/bin/bash
whois "$1" | awk -F: '/Registrant|Admin|Tech/ {gsub(/^[ \t]+/,"",$2); print $1","$2}' > "$1".csv
