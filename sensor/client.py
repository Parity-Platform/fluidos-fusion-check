import requests
import json

url = "http://46.101.126.196:8080:8080/sensor_values"

payload = json.dumps({
  # Add your data here
  "sensor_data": ""
})
headers = {
  'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)