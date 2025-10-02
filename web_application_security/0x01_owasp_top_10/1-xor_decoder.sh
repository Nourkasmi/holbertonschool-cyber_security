#!/bin/bash
# 1-xor_decoder.sh - Decodes WebSphere XOR encoded passwords
# Usage: ./1-xor_decoder.sh {xor}encoded_string

# Check if argument is provided
if [ $# -eq 0 ]
then
    echo "Usage: $0 {xor}encoded_string" >&2
    exit 1
fi

INPUT_STR="$1"

# Check if input starts with {xor}
case "$INPUT_STR" in
    {xor}*)
        # Remove the {xor} prefix (6 characters)
        ENCODED_STR="${INPUT_STR#\{xor\}}"
        ;;
    *)
        echo "Error: Input must start with {xor}" >&2
        exit 1
        ;;
esac

# Debug: show what we're decoding
echo "Decoding: $ENCODED_STR" >&2

# Base64 decode the string
BASE64_DECODED=$(echo -n "$ENCODED_STR" | base64 -d 2>/dev/null)

# Check if base64 decoding was successful
if [ $? -ne 0 ]
then
    echo "Error: Invalid Base64 encoding" >&2
    exit 1
fi

# WebSphere XOR key (0x5F in decimal is 95)
XOR_KEY=95
DECODED=""
LENGTH=${#BASE64_DECODED}
i=0

# XOR decode each character
while [ $i -lt $LENGTH ]
do
    CHAR="${BASE64_DECODED:$i:1}"
    ORD=$(printf "%d" "'$CHAR")
    XORED=$((ORD ^ XOR_KEY))
    DECODED_CHAR=$(printf "\\$(printf '%03o' "$XORED")")
    DECODED="${DECODED}${DECODED_CHAR}"
    i=$((i + 1))
done

# Output the decoded password
echo "$DECODED"