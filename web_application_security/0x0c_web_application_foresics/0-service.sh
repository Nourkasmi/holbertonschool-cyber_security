#!/bin/bash
grep "pam_unix" "auth.log" | sed -E 's/.*pam_unix\(([^)]+)\).*/\1/' | cut -d ':' -f1 | sort | uniq -c | sort -nr
