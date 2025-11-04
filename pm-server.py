import socket
import threading

def handle_client(client_socket, client_address):
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

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", 6767))
server_socket.listen(5)
print("Server listening on port 6767...")

while True:
    client_socket, client_address = server_socket.accept()
    # Create a new thread for each client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start()
