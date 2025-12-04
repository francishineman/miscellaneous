import requests
import json
import os


# TOKEN = 'Get token from: https://developer.webex.com/calling/docs/getting-started'
# This TOKEN is good for 12 hours. After that, you have to get a new token.

WEBEX_API_URL = "https://webexapis.com/v1/rooms"
WEBEX_ACCESS_TOKEN = TOKEN

HEADERS = {
"Authorization": f"Bearer {os.getenv('WEBEX_API_TOKEN')}",
"Content-Type": "application/json"
}

PAYLOAD = {
"name": "DevNet Associate Certification Team"
}

# response = requests.get(url=WEBEX_API_URL, headers=httpHeaders)
response = requests.request("POST", WEBEX_API_URL, data=json.dumps(PAYLOAD), headers=HEADERS)

print(response.text)

print(response.status_code)

print(json.dumps(response.json()))
