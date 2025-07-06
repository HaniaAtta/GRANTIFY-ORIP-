import os
import time
import requests
import paramiko
from dotenv import load_dotenv

# === Load secrets from .env ===
load_dotenv()
DO_API_TOKEN = os.getenv("DO_API_TOKEN")
SSH_KEY_ID = os.getenv("SSH_KEY_ID")
DROPLET_NAME = os.getenv("DROPLET_NAME", "grantify-scraper")
REGION = "nyc1"
IMAGE = "ubuntu-22-04-x64"
SIZE = "s-1vcpu-1gb"  # cheapest available
USER = "root"

# === 1. Create Droplet ===
print("[🚀] Creating droplet...")
headers = {
    "Authorization": f"Bearer {DO_API_TOKEN}",
    "Content-Type": "application/json",
}
droplet_data = {
    "name": DROPLET_NAME,
    "region": REGION,
    "size": SIZE,
    "image": IMAGE,
    "ssh_keys": [SSH_KEY_ID],
    "backups": False,
    "ipv6": False,
    "tags": ["grantify"],
}
response = requests.post("https://api.digitalocean.com/v2/droplets", headers=headers, json=droplet_data)
droplet = response.json().get("droplet")
droplet_id = droplet["id"]

print(f"[✅] Droplet {DROPLET_NAME} created with ID: {droplet_id}")

# === 2. Wait for IP assignment ===
ip = None
print("[⏳] Waiting for droplet IP...")
while not ip:
    time.sleep(5)
    resp = requests.get(f"https://api.digitalocean.com/v2/droplets/{droplet_id}", headers=headers)
    ip = resp.json()["droplet"]["networks"]["v4"][0]["ip_address"]

print(f"[🌐] Droplet IP: {ip}")

# === 3. Connect via SSH and Run start.sh ===
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

print("[🔑] Connecting via SSH...")
ssh.connect(ip, username=USER, key_filename=os.path.expanduser("~/.ssh/id_rsa"))  # Adjust path if needed

print("[⚙️] Uploading start.sh...")
sftp = ssh.open_sftp()
sftp.put("deployment/start.sh", "/root/start.sh")
sftp.chmod("/root/start.sh", 0o755)
sftp.close()

print("[🚦] Running script on droplet...")
stdin, stdout, stderr = ssh.exec_command("bash /root/start.sh")
print(stdout.read().decode())
print(stderr.read().decode())

ssh.close()

# === 4. Destroy Droplet ===
print("[🔥] Destroying droplet...")
destroy_url = f"https://api.digitalocean.com/v2/droplets/{droplet_id}"
requests.delete(destroy_url, headers=headers)

print("[✅] Done.")
