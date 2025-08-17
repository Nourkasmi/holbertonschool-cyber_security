for sub in $(cat subs.txt); do
    echo "$sub -> $(dig +short $sub | tail -n1)"
done > subdomain_ips.txt
