import requests
import json
import urllib3
from requests.auth import HTTPBasicAuth

# --- IMPORTANT CONFIGURATION ---
# WARNING: Self-signed certificates are common on network devices.
# The 'verify=False' flag bypasses certificate verification for simplicity,
# but you should replace 'verify=False' with 'verify=path/to/cert.pem' in production.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Replace these placeholders with your router's actual details
ROUTER_IP = "192.168.10.1"
PORT = 443  # Common ports: 443 (HTTPS), 8080 or 8443
BASE_URL = f"https://{ROUTER_IP}:{PORT}"

# Authentication credentials
USERNAME = "api_user"
PASSWORD = "your_strong_password"
AUTH = HTTPBasicAuth(USERNAME, PASSWORD)

# --- MOCK API ENDPOINTS ---
# You MUST consult your router's documentation (e.g., RESTCONF, eAPI)
# to get the correct paths for state data and configuration data.
OSPF_STATE_ENDPOINT = "/restconf/data/ietf-routing:routing/rib/ospf-state"
OSPF_CONFIG_ENDPOINT = "/restconf/data/ietf-routing:routing/routing-instance=default/ospf-config"


def get_ospf_state(url: str):
    """
    Retrieves the current operational state of OSPF from the router.
    """
    print(f"--- 1. FETCHING OSPF STATE FROM: {url} ---")
    try:
        # Use GET request for operational/state data
        response = requests.get(url, auth=AUTH, verify=False, timeout=10)

        # Check for successful response
        response.raise_for_status()

        # Assuming the response is JSON, format and print it
        state_data = response.json()
        print("Successfully retrieved OSPF State:")
        print(json.dumps(state_data, indent=4))

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: Could not retrieve OSPF state. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred during the request: {err}")


def configure_ospf(url: str):
    """
    Configures the router to join the company's OSPF network.
    """
    print(f"\n--- 2. CONFIGURING OSPF ON: {url} ---")

    # --- MOCK OSPF CONFIGURATION PAYLOAD ---
    # This payload structure is GENERIC and must be adjusted to match your device's
    # exact YANG model or API schema.
    ospf_configuration_payload = {
        "ospf": {
            "router-id": "1.1.1.1",
            "areas": [
                {
                    "area-id": "0.0.0.0",
                    "interfaces": [
                        {
                            "interface-name": "GigabitEthernet1",
                            "interface-type": "broadcast"
                        }
                    ],
                    # Advertise this network into OSPF Area 0
                    "network-statements": [
                        {
                            "ip-prefix": "192.168.50.0/24",
                            "type": "point-to-point"
                        }
                    ]
                }
            ]
        }
    }

    headers = {
        "Content-Type": "application/yang-data+json",
        "Accept": "application/yang-data+json"
    }

    try:
        # Use a PATCH request to apply configuration changes (idempotent update/merge)
        response = requests.patch(url, auth=AUTH, headers=headers, json=ospf_configuration_payload, verify=False, timeout=10)

        # Check for successful response (200, 201, 204 are common for config success)
        response.raise_for_status()

        if response.status_code == 204:
            print("Configuration successful (No Content).")
        elif response.status_code in [200, 201]:
            print(f"Configuration successful. Response: {response.text}")
        else:
            print(f"Unexpected success status code: {response.status_code}. Response: {response.text}")

    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: Configuration failed. Status code: {response.status_code}")
        print(f"Response text: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"An error occurred during the configuration request: {err}")


if __name__ == "__main__":
    # Full URLs for the specific requests
    state_url = BASE_URL + OSPF_STATE_ENDPOINT
    config_url = BASE_URL + OSPF_CONFIG_ENDPOINT

    # 1. Get the current OSPF state (Operational Data)
    get_ospf_state(state_url)

    # 2. Configure the OSPF network (Configuration Data)
    configure_ospf(config_url)
