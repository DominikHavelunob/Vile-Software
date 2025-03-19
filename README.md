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

Python **3.x** is required.

## **Future Improvements**
🔹 **Encryption & Secure Transmission**  
  - Use **AES encryption** to protect the payload from being intercepted.  
  - Each client would encrypt messages, and the server would decrypt them.

🔹 **Logging Enhancements**  
  - Store logs in **JSON** format for easier analysis.  
  - Optionally send logs to a remote server for centralized monitoring.

🔹 **Multithreading for the Server**  
  - Allow handling multiple ICMP clients simultaneously using Python’s `threading` module.  
  - Would improve performance when multiple devices send ICMP packets.

🔹 **IPv6 Support**  
  - Extend functionality to work over IPv6 (`socket.AF_INET6`).

🔹 **Graphical User Interface (GUI)**  
  - Develop a **simple GUI** to configure and launch the client/server.  
  - Could use **Tkinter, PyQt, or a web-based interface**.

## **Installation**
Clone this repository and navigate to the directory:
```sh
git clone https://github.com/DominikHavelunob/Vile-Software.git




