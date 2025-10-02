#!/bin/bash
# 1-xor_decoder.sh - Decodes WebSphere XOR encoded passwords

if [ $# -eq 0 ]
then
    echo "Usage: $0 {xor}encoded_string" >&2
    exit 1
fi

INPUT_STR="$1"
ENCODED_STR="${INPUT_STR:5}"

# Use Python for reliable byte handling
python3 -c "
import base64
import sys

encoded = '$ENCODED_STR'
decoded_bytes = base64.b64decode(encoded)
result = ''.join(chr(b ^ 0x5F) for b in decoded_bytes if b ^ 0x5F != 0)
print(result, end='')
"