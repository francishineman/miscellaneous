import requests
import json

WEBEX_API_TOKEN = "YOUR TOKEN HERE"
WEBEX_API_URL = "https://webexapis.com/v1/rooms"

if not WEBEX_API_TOKEN:
    print("ERROR: Webex API Token is missing or is the placeholder. Please set a valid token.")
    print("Get token from: https://developer.webex.com/calling/docs/getting-started.")
    print("Token is good for 12 hours. After that, you have to get a new token.")
    exit(1)

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
