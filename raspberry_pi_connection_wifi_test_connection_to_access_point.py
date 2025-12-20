import paramiko

def scan_wifi(client):
    print("Scanning for available Wi-Fi networks...")
    # --rescan yes ensures it doesn't just show cached results
    stdin, stdout, stderr = client.exec_command("nmcli --fields SSID,SIGNAL,SECURITY device wifi list --rescan yes")
    
    output = stdout.read().decode()
    if output:
        print("\nAvailable Networks:")
        print(output)
    else:
        print("No networks found. Or Error in scanning for Wi-Fi networks.")

def connect_wifi(client, ssid, wifi_password):
    print(f"Attempting to connect to '{ssid}'...")
    wifi_cmd = f"sudo nmcli device wifi connect '{ssid}' password '{wifi_password}'"
    
    stdin, stdout, stderr = client.exec_command(wifi_cmd)
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    if "successfully activated" in output:
        print(f"✅ Success: {output.strip()}")
    else:
        print(f"❌ Failed to connect:\n{error if error else output}")

def main():
    host = "10.0.0.123"
    user = "pi_test_user"
    password = "raspberry_passwd"
    
    target_ssid = "TestNetwork"
    target_pass = "TestPassword"

    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=user, password=password)

        scan_wifi(client)

        connect_wifi(client, target_ssid, target_pass)

        client.close()
    except Exception as e:
        print(f"Error encountered: {e}")

if __name__ == "__main__":
    main()
