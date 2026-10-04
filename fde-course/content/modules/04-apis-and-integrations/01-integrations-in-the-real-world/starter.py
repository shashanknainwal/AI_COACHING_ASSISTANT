import requests

BASE = "https://api.northwind.example"

session = requests.Session()
session.headers.update({"Authorization": "Bearer demo-token", "Accept": "application/json"})

response = session.get(f"{BASE}/v1/shipments", params={"limit": 50}, timeout=10)
print("Status:", response.status_code)
response.raise_for_status()

body = response.json()
for shipment in body["data"]:
    print(f"{shipment['id']}  {shipment['status']:<11} {shipment['origin']} -> {shipment['destination']}")
print("next_cursor:", body["next_cursor"])

# Try it:
#   1. Fetch one shipment:  session.get(f"{BASE}/v1/shipments/SHP-1003", timeout=10)
#   2. Request a path that doesn't exist, then call raise_for_status() and read the error.
