#!/bin/bash
grep -iE "/sbin/iptables -A INPUT" auth.log | wc -l
