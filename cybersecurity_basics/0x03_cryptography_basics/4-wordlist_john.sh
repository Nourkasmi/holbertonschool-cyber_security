#!/bin/bash
john --wordlist=/usr/share/wordlists/rockyou.txt --format=raw-md5 "$1"
john --show "$1" | cut -d: -f2 | head -n -2 > 4-password.txt