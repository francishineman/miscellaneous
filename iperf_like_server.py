import socket
import time
import sys

# Configuration
HOST = '0.0.0.0'  # Listen on all available interfaces
PORT = 5001       # Default port for iperf-like tests
BUFFER_SIZE = 65536  # 64 KB block size for efficient transfer

def start_server(host, port):
    """Initializes and runs the throughput server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allows the socket to be reused immediately after closing
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((host, port))
        server_socket.listen(1)
        print(f"--- Iperf-like Python Server (TCP) ---")
        print(f"Listening on {host}:{port}...")

        while True:
            # Wait for a connection
            conn, addr = server_socket.accept()
            print(f"Connection established with {addr}")

            total_bytes = 0
            start_time = time.time()
            
            # Start receiving data
            while True:
                try:
                    data = conn.recv(BUFFER_SIZE)
                except ConnectionResetError:
                    # Client abruptly closed the connection
                    print(f"Connection reset by client {addr}")
                    break

                if not data:
                    # Client closed the connection gracefully (EOF)
                    break
                
                total_bytes += len(data)

            end_time = time.time()
            conn.close()
            
            # Calculate results
            duration = end_time - start_time
            
            if duration > 0 and total_bytes > 0:
                # Convert bytes to megabits for iperf-style reporting
                total_megabits = (total_bytes * 8) / (1024 * 1024)
                throughput_mbps = total_megabits / duration
                
                print(f"--------------------------------------------------")
                print(f"Session Summary for {addr[0]}")
                print(f"  Transfer: {total_bytes / (1024*1024):.2f} MBytes")
                print(f"  Duration: {duration:.2f} seconds")
                print(f"  Bandwidth: {throughput_mbps:.2f} Mbps (Megabits per second)")
                print(f"--------------------------------------------------")
            else:
                print("No data received or transfer duration was too short.")
            
            print("Ready for next connection...")

    except socket.error as e:
        print(f"Socket error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_socket.close()

if __name__ == '__main__':
    start_server(HOST, PORT)
