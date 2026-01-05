#!/bin/bash
sudo nmap -sM -v -pftp,ssh,telnet,http,https $1