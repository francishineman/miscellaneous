import requests
import json

# Get token from: https://developer.webex.com/calling/docs/getting-started

WEBEX_API_URL = "https://webexapis.com/v1/rooms"
WEBEX_ACCESS_TOKEN = "GET_TOKEN_FROM"

httpHeaders = {'Authorization': 'Bearer ' + WEBEX_ACCESS_TOKEN}

response = requests.get(url=WEBEX_API_URL, headers=httpHeaders)

print(response.status_code)

print(json.dumps(response.json()))
