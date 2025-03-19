import socket
import struct
import os
import sys

# Function to print an ASCII art banner
def print_banner():
    """
    Prints an ASCII art banner at the start of the program.
    This enhances the visual presentation of the script and indicates its purpose.
    """
    banner = """
____   ____.__.__         .____________     _____ __________                                         
\   \ /   /|__|  |   ____ |   \_   ___ \   /     \\\______   \\  ______ ______________  __ ___________
 \   Y   / |  |  | _/ __ \|   /    \  \/  /  \ /  \|     ___/ /  ___// __ \_  __ \  \/ // __ \_  __ \\
  \     /  |  |  |_\  ___/|   \     \____/    Y    \    |     \___ \\\  ___/|  | \/\   /\  ___/|  | \/
   \___/   |__|____/\____>|___|\________/\____|____/____|____/______>\____>|__|    \_/  \____>|__|   
                                                                                                     
                                                                                                     
    """
    print(banner)

# Call the function to print the banner
print_banner()

# Class to define color codes for better console output readability
class Colors:
    """
    Defines ANSI escape sequences for colored text output.
    Used for highlighting important information like client IPs and payloads.
    """
    RED = '\033[31m'
    GREEN = '\033[32m'
    RESET = '\033[0m'

# Function to calculate the checksum for data integrity verification
def checksum(data):
    """
    Calculates the Internet checksum for a given data buffer.
    Ensures the integrity of ICMP packets by detecting corruption during transmission.

    Args:
        data (bytes): The data buffer to checksum.

    Returns:
        int: The calculated checksum value.
    """
    if len(data) % 2 != 0:
        data += b'\x00'  # Ensure even length by padding with a zero byte if necessary

    s = 0
    for i in range(0, len(data), 2):
        w = data[i] + (data[i+1] << 8)  # Combine two bytes into a 16-bit word
        s += w
        s = (s & 0xffff) + (s >> 16)  # Carry handling for checksum calculation

    return ~s & 0xffff

# Function to log client messages to a file
def log_message(client_ip, message):
    """
    Logs a message received from a client to a file specific to their IP address.
    The log file is named based on the client's IP, ensuring separation of logs.

    Args:
        client_ip (str): The IP address of the client.
        message (str): The message received from the client.
    """
    filename = f"client_{client_ip.replace('.', '_')}.txt"  # Replace dots with underscores for file safety
    with open(filename, 'a') as f:  # Open the file in append mode
        f.write(f"{message}\n")  # Write the message to the file
    print(f"Logged message from {Colors.RED}{client_ip}{Colors.RESET} to {filename}")

# Function to display a help message for the script's usage
def print_help():
    """
    Prints a help message showing the usage of the script and its command-line options.
    Useful for users unfamiliar with the script's functionality.
    """
    help_message = """
    Usage: python vile_server.py [options]

    Options:
    -r      Send ICMP echo reply
    -l      Enable logging
    -h      Show this help message and exit
    """
    print(help_message)

# Main function to handle ICMP communication
def main():
    """
    The main function of the server script. Listens for ICMP packets, processes them,
    and optionally sends replies or logs the communication based on user-provided options.
    """
    # Default settings: No response, no logging
    send_response = False
    logging_enabled = False

    # Parse command-line arguments
    args = sys.argv[1:]  # Exclude the script name
    if "-h" in args:  # Show help and exit if -h is provided
        print_help()
        sys.exit(0)

    if "-r" in args:  # Enable response mode if -r is provided
        send_response = True
    if "-l" in args:  # Enable logging if -l is provided
        logging_enabled = True

    # Create a raw socket to listen for ICMP packets
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    while True:
        # Receive an ICMP packet
        packet, addr = server_socket.recvfrom(1024)
        client_ip = addr[0]  # Extract the client's IP address
        print(f"Received packet from {Colors.RED}{client_ip}{Colors.RESET}")

        # Extract ICMP header and payload
        icmp_header = packet[20:28]  # ICMP header is located after the IP header
        icmp_payload = packet[28:]  # Payload starts immediately after the ICMP header

        # Handle odd-length payloads by padding with a zero byte
        if len(icmp_payload) % 2 != 0:
            icmp_payload += b'\x00'

        # Unpack the ICMP header fields
        icmp_type, code, checksum_val, packet_id, sequence = struct.unpack('bbHHh', icmp_header)

        print(f"ICMP Type: {icmp_type}, Code: {code}, Checksum: {checksum_val}, ID: {packet_id}, Sequence: {sequence}")
        payload_message = icmp_payload.decode(errors='ignore').strip()  # Decode the payload for display
        print(f"Payload from client: {Colors.GREEN}{payload_message}{Colors.RESET}")

        # Log the message to a file if logging is enabled
        if logging_enabled:
            log_message(client_ip, payload_message)

        # Send an ICMP echo reply if response mode is enabled and an echo request is received
        if icmp_type == 8 and send_response:  # Type 8 indicates an echo request
            print("Echo request received, sending reply")

            # Create the ICMP echo reply
            icmp_type = 0  # Type 0 indicates an echo reply
            code = 0  # No specific code for echo replies
            reply_payload = icmp_payload  # Echo the original payload back
            header = struct.pack('bbHHh', icmp_type, code, 0, packet_id, sequence)  # Build the ICMP header
            checksum_val = checksum(header + reply_payload)  # Recalculate the checksum
            header = struct.pack('bbHHh', icmp_type, code, socket.htons(checksum_val), packet_id, sequence)

            # Send the reply packet to the client
            server_socket.sendto(header + reply_payload, addr)
            print(f"Sent echo reply to {Colors.RED}{client_ip}{Colors.RESET}")

# Entry point of the script
if __name__ == "__main__":
    main()
