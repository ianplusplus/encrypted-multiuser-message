import socket
from security import encrypt, decrypt

HOST = '192.168.2.15'  # Localhost
PORT = 6767        # Port to listen on

# Create TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)
print(f"Server listening on {HOST}:{PORT}...")

client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address}")
client_input = ""
messages = []

while client_input != ":end":
# Receive data from client
    data = client_socket.recv(1024)
    client_input = data.decode()
    if client_input != ":end":
        messages.append(client_input)
    if data:
        print(f"Received from client: {data.decode()}")
        #client_socket.sendall(b"Hello, client!")  # Send response
print(f"Connection with {client_address} has ended.")
client_socket.close()

password = input("Enter password: ")

for message in messages:
    decoded_message = decrypt(message, password)
    print(decoded_message)