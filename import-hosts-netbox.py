import subprocess
import xml.etree.ElementTree as ET
import pynetbox
import requests
from mac_vendor_lookup import MacLookup

# Config
nmap_range = "192.168.1.0/24"
netbox_url = "https://http://192.168.1.144"
netbox_token = "4a8593d7bd6beb95f9574c575e95783d49b6b611"
discord_webhook = "https://discord.com/api/webhooks/1362175717827285022/v8ASU7JLvH7Y4effLy_xajDIc0IluGQKJn5fCOr4oJqJB3ynYBhr-bM-NeKp9hMciQov"

nb = pynetbox.api(netbox_url, token=netbox_token)
mac_lookup = MacLookup()

def send_discord_message(content):
    requests.post(discord_webhook, json={"content": content})

# Scan network
result = subprocess.run(["nmap", "-sn", "-oX", "-", nmap_range], capture_output=True, text=True)
root = ET.fromstring(result.stdout)

for host in root.findall("host"):
    ip_elem = host.find("address[@addrtype='ipv4']")
    mac_elem = host.find("address[@addrtype='mac']")

    if ip_elem is not None:
        ip = ip_elem.attrib["addr"]
        mac = mac_elem.attrib["addr"] if mac_elem is not None else "Unknown"
        vendor = "Unknown"
        
        if mac != "Unknown":
            try:
                vendor = mac_lookup.lookup(mac)
            except Exception:
                vendor = "Lookup failed"

        existing = nb.dcim.devices.filter(name=ip)
        if not existing:
            nb.dcim.devices.create(
                name=ip,
                device_type=1,  # Replace with actual device_type ID
                device_role=1,  # Replace with actual device_role ID
                site=1,         # Replace with actual site ID
                description=f"Discovered via script. MAC: {mac}, Vendor: {vendor}"
            )
            send_discord_message(f"New device discovered: {ip}\nMAC: {mac}\nVendor: {vendor}")

print("Scan completed.")
