// Throughput Test Program (iperf-like) in C++
// This program implements a simple network throughput test (server/client)
// using POSIX sockets and std::chrono for measurement.
//
// To compile (Linux/macOS): g++ iperf_clone.cpp -o iperf_clone -std=c++17
//
// Usage:
// Server: ./iperf_clone -s -p 5001
// Client: ./iperf_clone -c -h 127.0.0.1 -p 5001 -t 10
//

/**

g++ iperf_clone.cpp -o iperf_clone -std=c++17

1.  **Start the Server** in one terminal:
    ```bash
    ./iperf_clone -s -p 5001
    2.  **Start the Client** in a second terminal (it will run for 10 seconds by default):
    ```bash
    ./iperf_clone -c -h 127.0.0.1 -p 5001 -t 5
    
The client will send data for 5 seconds and report the throughput, and the server will report the received data and its calculated throughput. Let me know if you want to extend this with features like UDP testing or concurrent connections!
*/

#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <sstream>
#include <iomanip>

// POSIX Socket includes (Linux/macOS)
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>

using namespace std;

// --- Constants ---
const int DEFAULT_PORT = 5001;
const string DEFAULT_HOST = "127.0.0.1";
const int DEFAULT_DURATION = 10; // seconds
const size_t BUFFER_SIZE = 16384; // 16 KB

// --- Utility Functions ---

/**
 * @brief Converts bytes to a human-readable string (e.g., 1024 to "1.00 KB").
 * @param bytes The number of bytes.
 * @return A formatted string.
 */
string format_bytes(long long bytes) {
    static const vector<string> SIZES = {"B", "KB", "MB", "GB", "TB"};
    double len = static_cast<double>(bytes);
    int i = 0;
    while (len >= 1024.0 && i < SIZES.size() - 1) {
        len /= 1024.0;
        i++;
    }
    stringstream ss;
    ss << fixed << setprecision(2) << len << " " << SIZES[i];
    return ss.str();
}

/**
 * @brief Reports the final throughput statistics.
 * @param bytes_transferred Total bytes sent/received.
 * @param duration_s Total duration in seconds.
 */
void report_stats(long long bytes_transferred, double duration_s) {
    if (duration_s <= 0) duration_s = 1e-9; // Avoid division by zero
    
    double bits_transferred = static_cast<double>(bytes_transferred) * 8.0;
    double mbps = (bits_transferred / duration_s) / (1000.0 * 1000.0); // Mbits/s
    double gbp = (bits_transferred / duration_s) / (1000.0 * 1000.0 * 1000.0); // Gbits/s

    cout << "-----------------------------------------------------------" << endl;
    cout << "Transfer complete." << endl;
    cout << "Duration: " << fixed << setprecision(2) << duration_s << " s" << endl;
    cout << "Bytes:    " << format_bytes(bytes_transferred) << endl;
    
    cout << "Throughput: ";
    if (gbp >= 1.0) {
        cout << fixed << setprecision(2) << gbp << " Gbits/s" << endl;
    } else {
        cout << fixed << setprecision(2) << mbps << " Mbits/s" << endl;
    }
    cout << "-----------------------------------------------------------" << endl;
}

// --- Server Implementation ---

/**
 * @brief Runs the throughput server.
 * @param port The port to listen on.
 */
void run_server(int port) {
    cout << "Starting server on port " << port << "..." << endl;

    // 1. Create socket file descriptor
    int listen_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (listen_fd < 0) {
        cerr << "ERROR: Failed to create listening socket." << endl;
        return;
    }
    
    // Optional: Set socket options to reuse address
    int opt = 1;
    setsockopt(listen_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    // 2. Bind the socket to the port
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(port);

    if (bind(listen_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        cerr << "ERROR: Failed to bind socket to port " << port << ". Address already in use or permission denied." << endl;
        close(listen_fd);
        return;
    }

    // 3. Listen for incoming connections
    if (listen(listen_fd, 5) < 0) {
        cerr << "ERROR: Failed to listen on socket." << endl;
        close(listen_fd);
        return;
    }

    cout << "Server listening. Waiting for a connection..." << endl;

    // 4. Accept the connection
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    int client_fd = accept(listen_fd, (struct sockaddr*)&client_addr, &client_len);
    
    // Close listening socket after accepting one connection (simpler iperf model)
    close(listen_fd); 

    if (client_fd < 0) {
        cerr << "ERROR: Failed to accept connection." << endl;
        return;
    }
    
    string client_ip = inet_ntoa(client_addr.sin_addr);
    int client_port = ntohs(client_addr.sin_port);
    cout << "Connection accepted from " << client_ip << ":" << client_port << endl;
    cout << "Receiving data..." << endl;

    // 5. Receive data and calculate stats
    long long total_bytes_received = 0;
    vector<char> buffer(BUFFER_SIZE);
    
    // Start measuring time only when the first packet arrives
    auto start_time = chrono::high_resolution_clock::now();
    bool first_read = true;
    double duration_s = 0.0;
    
    while (true) {
        ssize_t bytes_read = recv(client_fd, buffer.data(), BUFFER_SIZE, 0);
        
        if (first_read && bytes_read > 0) {
            start_time = chrono::high_resolution_clock::now();
            first_read = false;
        }

        if (bytes_read > 0) {
            total_bytes_received += bytes_read;
        } else if (bytes_read == 0) {
            // Client closed the connection
            cout << "Client disconnected." << endl;
            break;
        } else {
            // Error
            cerr << "ERROR during receive." << endl;
            break;
        }
    }

    // End time measurement
    if (!first_read) {
        auto end_time = chrono::high_resolution_clock::now();
        duration_s = chrono::duration<double>(end_time - start_time).count();
    }
    
    // 6. Report results
    if (total_bytes_received > 0) {
        report_stats(total_bytes_received, duration_s);
    } else {
        cout << "No data was received." << endl;
    }

    // 7. Cleanup
    close(client_fd);
}

// --- Client Implementation ---

/**
 * @brief Runs the throughput client.
 * @param host The server IP address.
 * @param port The server port.
 * @param duration_s The duration to send data for.
 */
void run_client(const string& host, int port, int duration_s) {
    cout << "Starting client. Connecting to " << host << ":" << port << " for " << duration_s << " seconds..." << endl;

    // 1. Create socket file descriptor
    int client_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (client_fd < 0) {
        cerr << "ERROR: Failed to create client socket." << endl;
        return;
    }

    // 2. Resolve server address
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(port);
    
    if (inet_pton(AF_INET, host.c_str(), &server_addr.sin_addr) <= 0) {
        cerr << "ERROR: Invalid address or address not supported: " << host << endl;
        close(client_fd);
        return;
    }

    // 3. Connect to the server
    if (connect(client_fd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        cerr << "ERROR: Connection failed. Check server IP/Port and if server is running." << endl;
        close(client_fd);
        return;
    }

    cout << "Connection established. Sending data..." << endl;

    // 4. Send data loop
    long long total_bytes_sent = 0;
    vector<char> buffer(BUFFER_SIZE, 'A'); // Filler data
    
    auto start_time = chrono::high_resolution_clock::now();
    auto end_test_time = start_time + chrono::seconds(duration_s);
    
    // Use a high-resolution timer for sending loop
    while (chrono::high_resolution_clock::now() < end_test_time) {
        ssize_t bytes_sent = send(client_fd, buffer.data(), BUFFER_SIZE, 0);
        
        if (bytes_sent > 0) {
            total_bytes_sent += bytes_sent;
        } else if (bytes_sent < 0) {
            cerr << "ERROR during send. Aborting test." << endl;
            break;
        }
        // If bytes_sent == 0, the socket might be non-blocking or shut down,
        // but since we are blocking, 0 or less than requested indicates an issue.
    }
    
    auto final_time = chrono::high_resolution_clock::now();
    double actual_duration = chrono::duration<double>(final_time - start_time).count();

    // 5. Cleanup
    close(client_fd);
    
    // 6. Report results
    if (total_bytes_sent > 0) {
        report_stats(total_bytes_sent, actual_duration);
    } else {
        cout << "No data was sent." << endl;
    }
}

// --- Main Function (Argument Parsing) ---

void display_usage(const string& program_name) {
    cout << "Usage:" << endl;
    cout << "  Server Mode: " << program_name << " -s [-p <port>]" << endl;
    cout << "  Client Mode: " << program_name << " -c -h <host> [-p <port>] [-t <seconds>]" << endl;
    cout << endl;
    cout << "Options:" << endl;
    cout << "  -s : Run in server mode." << endl;
    cout << "  -c : Run in client mode." << endl;
    cout << "  -h : Server hostname or IP address (client mode only). Default: " << DEFAULT_HOST << endl;
    cout << "  -p : Server port to listen/connect to. Default: " << DEFAULT_PORT << endl;
    cout << "  -t : Time in seconds to transmit data (client mode only). Default: " << DEFAULT_DURATION << endl;
    cout << "  -? or --help : Display this usage message." << endl;
    cout << endl;
}

int main(int argc, char* argv[]) {
    string program_name = argv[0];
    bool is_server = false;
    bool is_client = false;
    string host = DEFAULT_HOST;
    int port = DEFAULT_PORT;
    int duration = DEFAULT_DURATION;

    // Simple argument parsing loop
    for (int i = 1; i < argc; ++i) {
        string arg = argv[i];

        if (arg == "-s") {
            is_server = true;
        } else if (arg == "-c") {
            is_client = true;
        } else if (arg == "-h" && i + 1 < argc) {
            host = argv[++i];
        } else if (arg == "-p" && i + 1 < argc) {
            try {
                port = stoi(argv[++i]);
            } catch (...) {
                cerr << "ERROR: Invalid port number provided." << endl;
                return 1;
            }
        } else if (arg == "-t" && i + 1 < argc) {
            try {
                duration = stoi(argv[++i]);
            } catch (...) {
                cerr << "ERROR: Invalid duration provided." << endl;
                return 1;
            }
        } else if (arg == "-?" || arg == "--help") {
            display_usage(program_name);
            return 0;
        } else {
            cerr << "ERROR: Unknown or incomplete argument: " << arg << endl;
            display_usage(program_name);
            return 1;
        }
    }

    if (is_server == is_client) {
        cerr << "ERROR: Must specify either server (-s) or client (-c) mode, but not both or neither." << endl;
        display_usage(program_name);
        return 1;
    }

    if (is_server) {
        run_server(port);
    } else { // is_client
        if (host.empty()) {
            cerr << "ERROR: Client mode requires a host/IP address (-h)." << endl;
            return 1;
        }
        run_client(host, port, duration);
    }

    return 0;
}
