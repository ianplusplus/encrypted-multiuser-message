import socket
from security import encrypt, decrypt

HOST = '192.168.2.15'  # Server IP
PORT = 6767        # Server port

# Create TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))  # Connect to server

password = input("Enter password: ")

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