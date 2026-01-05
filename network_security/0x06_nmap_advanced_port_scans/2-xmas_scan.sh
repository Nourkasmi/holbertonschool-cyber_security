#!/bin/bash
sudo nmap -sX -p440-450 --reason --open --packet-trace $1