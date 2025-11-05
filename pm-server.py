import socket
import threading
import argparse
from messages import recv_message, send_message

session_data = {}
socket_map = {}

def handle_client(client_socket, client_address):
    global session_data
    global socket_map
    
    session_id = recv_message(client_socket)
    client_id = recv_message(client_socket)

    print(f"Connection {client_address}, Session ID: {session_id}, Client ID: {client_id}")

    if session_id not in session_data:
        session_data[session_id] = []
    session_data[session_id].append(client_id)

    if client_id not in socket_map:
        socket_map[client_id] = client_socket

    client_input = ""

    end = False

    while not end:
        try:
            # Receive a new message from this client
            message = recv_message(client_socket)
            if not message:
                break

            print(f"{client_id} says: {message}")

            # Broadcast to other clients in same session/group
            for other_client in session_data[session_id]:
                if other_client != client_id:
                    send_message(socket_map[other_client], f"{client_id}: {message}")

        except Exception as e:
            print("Error:", e)
            break

    print(f"Connection with {client_address} has ended.")

    if client_socket in socket_map:
        del socket_map[client_id]
    if client_id in session_data[session_id]:
        session_data[session_id].remove(client_id)


    client_socket.close()

parser = argparse.ArgumentParser(description="Port-Message Server")

parser.add_argument("--port", "-p", type=int, default=6767, help="Listening port for server.")
args = parser.parse_args()

port = args.port

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", port))
server_socket.listen(5)
print(f"Server listening on port {port}...")

running = True

def command_listener():
    global running
    while running:
        cmd = input()
        if cmd.lower() == ":end":
            running = False
            print("Stopping server...")
            server_socket.close()

# Start the command listener thread
threading.Thread(target=command_listener, daemon=True).start()

while running:
    client_socket, client_address = server_socket.accept()
    # Create a new thread for each client
    client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
    client_thread.start() 
