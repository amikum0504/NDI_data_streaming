import requests
from json import loads
import json

url = " https://webexapis.com/v1/rooms?type=group"

headers = {
    'Authorization': 'Bearer <your_API_Token>', #Replace with your_API_Token
    'Content-Type': 'application/json'
}
# Define the data variable, even if not used
data = {}

# Send GET request
response = requests.get(url, headers=headers, data=json.dumps(data))

# Check for HTTP response status
if response.status_code == 200:
    # Parse and pretty print the response JSON
    print(json.dumps(response.json(), sort_keys=True, indent=4))
else:
    # Print error information
    print(f"Error: {response.status_code} - {response.text}")
