import requests
import json

# TOKEN = 'Get token from: https://developer.webex.com/calling/docs/getting-started'
# This TOKEN is good for 12 hours. After that, you have to get a new token.
WEBEX_API_TOKEN = "YOUR TOKEN HERE"
WEBEX_API_URL = "https://webexapis.com/v1/rooms"

HEADERS = {
    "Authorization": f"Bearer {WEBEX_API_TOKEN}",
    "Content-Type": "application/json"
}

PAYLOAD = {
    "title": "Performance Test, Team Meeting"
}

try:
    response = requests.request("POST", WEBEX_API_URL, data=json.dumps(PAYLOAD), headers=HEADERS)

    print(f"\nHTTP Status Code: {response.status_code}\n")

    if response.status_code // 100 == 2:
        print("Successfully created the Webex meeting!")
        print(json.dumps(response.json(), indent=4))
    else:
        print("API request failed!")
        print("Error Details: (Response Text): (response.text)")

except requests.exceptions.RequestException as e:
    print(f"A network error occurred: {e}")
except json.JSONDecodeError:
    print("Warning: Could not decode response as JSON.")
    print(f"Raw Response Text: {response.text}")

print(f"\nHTTP Status Code: {response.status_code}")
print(json.dumps(response.json(), indent=4))
