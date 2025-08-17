# Holbertonschool.com Passive Reconnaissance Report

## 1. IP Ranges & WHOIS
- **Registrar**: Gandi SAS
- **Registrant**: Holberton Inc (Los Angeles, US)
- **Creation Date**: 2015-07-30
- **Expiration Date**: 2026-07-30
- **Name Servers**:
  - ns-957.awsdns-55.net
  - ns-1244.awsdns-27.org
  - ns-1991.awsdns-56.co.uk
  - ns-343.awsdns-42.com

**Observed IPs (A records)**:
- 75.2.70.75
- 99.83.190.102
- (via Cloudflare proxy also: 35.152.117.67)

---

## 2. Subdomains & DNS Records
From **dig / nslookup** and DNS TXT records:
- `www.holbertonschool.com` → Main site
- `holbertonschool.com` → Redirects to `www`
- MX records (email service):
  - `aspmx.l.google.com`
  - `alt1.aspmx.l.google.com`
  - `alt2.aspmx.l.google.com`
  - `alt3.aspmx.l.google.com`
  - `alt4.aspmx.l.google.com`
- TXT records:
  - SPF: `v=spf1 include:mailgun.org include:_spf.google.com -all`
  - `stripe-verification=...`
  - `zapier-domain-verification=...`
  - `google-site-verification=...`
  - `brevo-code=...`
  - `loaderio=...`
  - `intacct-esk=...`

---

## 3. Technologies & Frameworks

From **curl -I**:
- **Web Server**: Cloudflare (reverse proxy / CDN)
- **Security Headers**:
  - HSTS (Strict-Transport-Security)
  - CSP (Content-Security-Policy)
  - X-Frame-Options: SAMEORIGIN

From **whatweb**:
- **Initial Server**: nginx (redirects)
- **Frameworks / Libraries**:
  - OpenResty
  - JQuery
  - HTML5
  - Open Graph Protocol (meta)
- **Infrastructure**:
  - Cloudflare (WAF/CDN)
  - AWS (NS & IP delegation)

---

## 4. Notes
- Shodan CLI was not usable due to account restrictions (Free plan, 0 credits → 403 Forbidden).
- Reconnaissance completed with:
  - WHOIS
  - dig / nslookup
  - curl (headers)
  - whatweb (fingerprinting)
- Results show that holbertonschool.com uses **Cloudflare**, runs via **nginx/OpenResty**, and relies on **Google Workspace** for email.
