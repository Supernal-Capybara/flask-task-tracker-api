
import requests

BASE_URL = "http://127.0.0.1:5000"

update_personnel = {"assigned_to": "william ransome",
                 "task_name": "wipe propulsion data"}

response = requests.patch(f"{BASE_URL}/tasks/4", json=update_personnel)


print("Status code:", response.status_code)
print("Raw response text:", response.text)

try:
    print("Response JSON:", response.json())
except requests.exceptions.JSONDecodeError:
    print("Response was not valid JSON.")
    