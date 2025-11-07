import socket
import threading
import argparse
import time
from security import encrypt, decrypt
from messages import recv_message, send_message
from akey import generate_encrypted_ed25519_keypair, load_private_key, load_public_key, file_exists

running = True  # Main flag to control program
connected = False  # Flag to check if socket is connected

# -------------------------------
# Thread to receive messages
# -------------------------------
def receive(sock, passwd):
    global running, connected
    while running and connected:
        try:
            data = recv_message(sock)
            if not data:
                print("Server closed connection.")
                connected = False
                break

            split_data = data.split(" ")
            if len(split_data) < 2:
                continue

            plain_text = decrypt(split_data[1], passwd)
            print(f"{split_data[0]} {plain_text}")

        except Exception:
            connected = False
            break

# -------------------------------
# Thread to send messages
# -------------------------------
def send(sock, passwd):
    global running, connected
    print("Enter messages. Type ':end' to quit.")

    while running:
        try:
            user_input = input()
            if user_input.strip() == ":end":
                running = False
                break
            if connected:
                encrypted_msg = encrypt(user_input, passwd)
                send_message(sock, encrypted_msg)
            else:
                print("Not connected to server. Waiting to reconnect...")
        except Exception:
            connected = False
            time.sleep(1)

# -------------------------------
# Main client logic
# -------------------------------
parser = argparse.ArgumentParser(description="Port-Message Client")
parser.add_argument("--address", "-a", help="Server address")
parser.add_argument("--port", "-p", type=int, default=6767, help="Server port")
parser.add_argument("--secret", "-s", help="Password")
parser.add_argument("--id", "-i", help="Session ID")
parser.add_argument("--name", "-n", help="Client unique ID")
parser.add_argument("--key", "-k", help="Creates a new key pair for the client/session combination.", action="store_true")
args = parser.parse_args()

HOST = args.address
PORT = args.port
password = args.secret or input("Enter password: ")
sessionid = args.id or input("Enter the session id: ")
clientname = args.name or input("Enter your unique name: ")

if args.key or not file_exists("{clientname}.{sessionid}_private_ed25519.pem"):
    generate_encrypted_ed25519_keypair(f"{clientname}.{sessionid}_private_ed25519.pem", f"{clientname}.{sessionid}_public_ed25519.pem")

# -------------------------------
# Reconnect loop
# -------------------------------
while running:
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        connected = True
        print(f"Connected to {HOST}:{PORT}")

        # Send session info
        send_message(client_socket, sessionid)
        send_message(client_socket, clientname)

        # Start threads for sending and receiving
        recv_thread = threading.Thread(target=receive, args=(client_socket, password), daemon=True)
        send_thread = threading.Thread(target=send, args=(client_socket, password), daemon=True)
        recv_thread.start()
        send_thread.start()

        # Wait for threads to finish
        while running and connected:
            time.sleep(0.1)

        if not running:
            break

        print("Disconnected from server. Attempting to reconnect in 5 seconds...")
        try:
            client_socket.close()
        except:
            pass
        time.sleep(5)

    except Exception as e:
        print(f"Connection failed: {e}. Retrying in 5 seconds...")
        time.sleep(5)

# Cleanup
try:
    client_socket.close()
except:
    pass

print("Client exited.")
