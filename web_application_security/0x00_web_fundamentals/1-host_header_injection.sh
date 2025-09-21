#!/bin/bash
curl -s -i -X POST -H "Host: $1" --data "$3" "$2" | sed -n '1,200p'
