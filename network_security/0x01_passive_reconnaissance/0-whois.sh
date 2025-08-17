#!/bin/bash
whois $1 | awk '/Registrant|Admin|Tech/ && /Organization|State|Country|Email/ {gsub(": ",","); print}' > $1.csv
