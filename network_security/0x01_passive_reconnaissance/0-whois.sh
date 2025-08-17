#!/bin/bash
whois $1 | awk '/Registrant|Admin|Tech/ {gsub(": ",","); print}' > $1.csv
