import socket
import time
import sys
import argparse

# Configuration
BUFFER_SIZE = 65536  # 64 KB block size for sending data
DEFAULT_HOST = '127.0.0.1' # Default to localhost
DEFAULT_PORT = 5001
DEFAULT_DURATION = 10 # seconds

def run_client(host, port, duration):
    """Connects to the server and sends data for a specified duration."""
    
    # Create a dummy data block for transfer
    # Using 'b' prefix for bytes literal. This block is 64KB.
    data_block = b'A' * BUFFER_SIZE
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"--- Iperf-like Python Client (TCP) ---")
        print(f"Connecting to {host}:{port}...")
        client_socket.connect((host, port))
        
        total_bytes_sent = 0
        
        start_time = time.time()
        end_test_time = start_time + duration

        # Start sending loop
        while time.time() < end_test_time:
            # We use sendall to ensure all data is sent, handling any partial sends internally
            client_socket.sendall(data_block)
            total_bytes_sent += BUFFER_SIZE

        # Test duration reached
        final_time = time.time()
        actual_duration = final_time - start_time
        
        # Close the connection to signal the server that the transfer is complete
        client_socket.close()

        # Final Client-Side Calculation
        if actual_duration > 0 and total_bytes_sent > 0:
            total_megabits = (total_bytes_sent * 8) / (1024 * 1024)
            throughput_mbps = total_megabits / actual_duration
            
            print(f"--------------------------------------------------")
            print(f"Client Session Complete")
            print(f"  Transfer: {total_bytes_sent / (1024*1024):.2f} MBytes")
            print(f"  Duration: {actual_duration:.2f} seconds")
            print(f"  Bandwidth: {throughput_mbps:.2f} Mbps (Megabits per second)")
            print(f"--------------------------------------------------")
        else:
            print("Transfer failed or no data sent.")

    except socket.error as e:
        print(f"Connection error: Could not connect to the server at {host}:{port}.")
        print(f"Details: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nClient stopped manually.")
    finally:
        if 'client_socket' in locals() and client_socket.fileno() != -1:
            client_socket.close()

if __name__ == '__main__':
    # Use argparse for a clean command-line interface
    parser = argparse.ArgumentParser(description="Python Iperf-like TCP Client.")
    parser.add_argument('host', nargs='?', default=DEFAULT_HOST, help="The IP address of the server.")
    parser.add_argument('-t', '--time', type=int, default=DEFAULT_DURATION, help="Time in seconds to transmit data (default: 10).")
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT, help="Server port (default: 5001).")
    
    args = parser.parse_args()
    
    run_client(args.host, args.port, args.time)
