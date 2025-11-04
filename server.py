import socket
import argparse
from security import encrypt, decrypt

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't even need to connect successfully
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

parser = argparse.ArgumentParser(description="Port-Message Server")

parser.add_argument("--port", "-P", type=int, default=6767, help="Listening port for server.")
args = parser.parse_args()

HOST = get_local_ip()  # Localhost
PORT = args.port        # Port to listen on

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

print('---------------------------------------------------------------------------------------')
print('SECRET --- SECRET --- SECRET --- SECRET --- SECRET --- SECRET --- SECRET --- SECRET ---')
print('---------------------------------------------------------------------------------------')

for message in messages:
    decoded_message = decrypt(message, password)
    print(decoded_message)
