# ICMP Client-Server Communication

This project implements an ICMP-based communication system using raw sockets. The client sends ICMP Echo Request packets with a custom payload, and the server listens for incoming packets, optionally logging messages and sending ICMP Echo Reply packets.

## Features
- **Client:**
  - Sends ICMP echo requests with customizable payloads.
  - Supports payload padding to match Linux or Windows behavior.
  - Options for silent mode and disabling server response.
- **Server:**
  - Listens for ICMP echo requests.
  - Optionally logs client messages to a file.
  - Can respond with ICMP echo replies.

## **Prerequisites**
Since this script uses raw sockets, it **requires administrative privileges**:
- **Linux/macOS:** Run the script with `sudo`
- **Windows:** Run the script in an administrator Command Prompt

Python **3.x** is required.

## **Installation**
Clone this repository and navigate to the directory:
```sh
git clone https://github.com/DominikHavelunob/Vile-Software.git

