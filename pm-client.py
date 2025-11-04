import socket
import argparse
from security import encrypt, decrypt

parser = argparse.ArgumentParser(description="Port-Message Client")

parser.add_argument("--address", "-a", help="Address of the server.")
parser.add_argument("--port", "-p", type=int, default=6767, help="Listening port for server.")
parser.add_argument("--secret", "-s", help="Sets the password")
parser.add_argument("--id", "-i", help="Session ID for the communication")
args = parser.parse_args()

HOST = args.address  # Server IP
PORT = args.port        # Server port

# Create TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))  # Connect to server

if args.secret == None:
    password = input("Enter password: ")
else:
    password = args.secret

if args.id == None:
    id = input("Enter the session id: ")
else:
    password = args.id
    
print("Enter in messages. Press enter to send message. Send ':end' to end communication.")

user_input = input()
if user_input != ":end":
    user_input = encrypt(user_input, password)

while user_input != ":end":
    client_socket.sendall(user_input.encode())
    user_input = input()
    if user_input != ":end":
        user_input = encrypt(user_input, password)
client_socket.sendall(user_input.encode())

client_socket.close()