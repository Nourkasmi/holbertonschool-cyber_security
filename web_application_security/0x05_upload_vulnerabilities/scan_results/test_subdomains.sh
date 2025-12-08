#!/bin/bash
echo "Testing each subdomain for web content..."
echo ""

while read subdomain; do
    echo "=== Testing: $subdomain.web0x05.hbtn ==="
    
    # Get HTTP status
    status=$(curl -s -o /dev/null -w "%{http_code}" -I "http://$subdomain.web0x05.hbtn" --connect-timeout 5)
    
    if [ "$status" != "000" ] && [ "$status" != "404" ] && [ "$status" != "403" ]; then
        echo "Status: $status"
        
        # Get page title
        title=$(curl -s "http://$subdomain.web0x05.hbtn" | grep -o '<title>[^<]*</title>' | sed 's/<title>//;s/<\/title>//')
        [ -n "$title" ] && echo "Title: $title"
        
        # Check for upload forms
        has_upload=$(curl -s "http://$subdomain.web0x05.hbtn" | grep -i "type=\"file\"\|upload\|multipart" | head -1)
        if [ -n "$has_upload" ]; then
            echo "POTENTIAL UPLOAD FEATURE FOUND!"
            echo "UPLOAD SUBDOMAIN: $subdomain.web0x05.hbtn" > ../upload_target.txt
        fi
        
        echo ""
    else
        echo "Status: $status (skipping)"
        echo ""
    fi
    
    sleep 1  # Be nice to the server
done < discovered_subdomains.txt

echo ""
echo "=== TEST COMPLETE ==="
if [ -f ../upload_target.txt ]; then
    echo "Upload target found:"
    cat ../upload_target.txt
else
    echo "No obvious upload features found in subdomain names."
fi
