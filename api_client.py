
import requests

BASE_URL = "http://127.0.0.1:5000"

update_personnel = {"assigned_to": "william ransome",
                 "task_name": "wipe propulsion data"}

add_personnel = {"task_name": "synthetic rocket fuel test",
                 "priority": "urgent", "status": "completed",
                 "assigned_to": "Lily Peskova"}

# response = requests.patch(f"{BASE_URL}/tasks/4", json=update_personnel)

response = requests.post(f"{BASE_URL}/tasks", json=add_personnel)

print("Status code:", response.status_code)
print("Raw response text:", response.text)

try:
    print("Response JSON:", response.json())
except requests.exceptions.JSONDecodeError:
    print("Response was not valid JSON.")
    