import re
import getpass
from netmiko import ConnectHandler, NetmikoAuthenticationException, NetmikoTimeoutException
import pyats
import genie
import rich

# --- Configuration: Replace these placeholders with your actual device details ---
DEVICE_IP = "192.168.1.1"  # Replace with the device's IP address or hostname
DEVICE_TYPE = "cisco_ios" # Use "cisco_ios" or "cisco_xe" as appropriate
USERNAME = "your_username"
PASSWORD = "your_password" # It is safer to prompt for credentials

# Uptime threshold in hours (8 hours)
UPTIME_THRESHOLD_HOURS = 8

def convert_uptime_to_hours(uptime_str):
    """
    Converts a human-readable uptime string (e.g., '2 weeks, 5 days, 4 hours')
    to a total number of hours.

    Args:
        uptime_str (str): The uptime string returned by the Genie parser.

    Returns:
        float: The total uptime in hours.
    """
    if not uptime_str:
        return 0.0

    total_minutes = 0
    # Map time units to their value in minutes
    conversion_factors = {
        'year': 525600, # 365 * 24 * 60
        'week': 10080,  # 7 * 24 * 60
        'day': 1440,    # 24 * 60
        'hour': 60,
        'minute': 1
    }

    # Look for patterns like 'N unit(s)' in the string
    for unit, minutes in conversion_factors.items():
        # This regex handles both singular and plural (e.g., '1 day' or '5 days')
        pattern = rf'(\d+)\s+{unit}'
        match = re.search(pattern, uptime_str, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            total_minutes += value * minutes

    return total_minutes / 60.0


def check_router_uptime(ip, device_type, username, password):
    """
    Connects to the device, retrieves the uptime using Genie parsing, and
    checks if it's below the 8-hour threshold.
    """
    device = {
        "device_type": device_type,
        "host": ip,
        "username": username,
        "password": password,
    }

    print(f"--- Attempting connection to {ip} ({device_type}) ---")

    try:
        # Netmiko handles the SSH connection
        net_connect = ConnectHandler(**device)
        print("Connection successful.")

        # Execute 'show version' and use pyATS Genie parser (use_genie=True)
        # This returns a structured Python dictionary instead of raw text.
        # The command must be a valid command with an existing Genie parser.
        parsed_output = net_connect.send_command(
            "show version",
            use_genie=True,
            read_timeout=60 # Increase timeout for complex commands
        )

        net_connect.disconnect()
        print("Disconnected from device.")

        # The structure for Cisco IOS/IOS-XE generally puts uptime here.
        # Check if the 'uptime' key exists in the parsed output's 'version' section.
        uptime_str = parsed_output.get("version", {}).get("uptime", None)

        if not uptime_str:
            print("ERROR: Could not find 'uptime' key in the Genie parsed output. Parser structure may differ.")
            return

        # Convert the human-readable string to hours
        uptime_hours = convert_uptime_to_hours(uptime_str)

        print(f"\nDevice Uptime (Raw): {uptime_str}")
        print(f"Device Uptime (Hours): {uptime_hours:.2f} hours")
        print(f"Threshold: {UPTIME_THRESHOLD_HOURS} hours")

        # Check the condition
        if uptime_hours < UPTIME_THRESHOLD_HOURS:
            print("\n🚨 WARNING: ROUTER RECENTLY REBOOTED!")
            print(f"The router has been up for less than {UPTIME_THRESHOLD_HOURS} hours.")
        else:
            print("\n✅ Router is up.")

    except NetmikoAuthenticationException:
        print("\nERROR: Authentication failed. Check username and password.")
    except NetmikoTimeoutException:
        print(f"\nERROR: Connection timed out to {ip}. Check IP and network reachability.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    # In a real environment, you would prompt for the password for security
    # router_password = getpass.getpass(prompt="Enter password: ")
    # check_router_uptime(DEVICE_IP, DEVICE_TYPE, USERNAME, router_password)

    # For a placeholder, use the hardcoded variables above
    # NOTE: You MUST update DEVICE_IP, USERNAME, and PASSWORD/SECRET for this to run
    # against a real device.
    check_router_uptime(DEVICE_IP, DEVICE_TYPE, USERNAME, PASSWORD)

    # --- Mocking Example (for testing the logic without a device) ---
    # uptime_short = "1 hour, 35 minutes"
    # uptime_long = "2 weeks, 5 days, 10 hours"
    # uptime_just_over = "8 hours, 1 minute"

    # print("\n--- Uptime Conversion Tests ---")
    # print(f"'{uptime_short}' -> {convert_uptime_to_hours(uptime_short):.2f} hours")
    # print(f"'{uptime_long}' -> {convert_uptime_to_hours(uptime_long):.2f} hours")
    # print(f"'{uptime_just_over}' -> {convert_uptime_to_hours(uptime_just_over):.2f} hours")
    # print("-------------------------------")



"""
#Example, before and after:

from netmiko import ConnectionHandler
import pyats
import genie
import rich

host = 'bldg_119_floor_121'
user = 'admin'
password = 'cisco123'
type = 'cisco_xe'

rtr_1 = ConnectionHandler(host=host, username=user, password=password, device_type=type)

response = rtr_1.send_command("show version", use_genie=True)

#pretty.pprint(response)

up_time = response['version']['uptime']

print(f"The uptime of the router is: {up_time}.")

"""
