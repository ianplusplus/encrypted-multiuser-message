import socket
import threading
import argparse
from messages import recv_message, send_message

session_data = {}
socket_map = {}

session_lock = threading.Lock()
socket_lock = threading.Lock()

def handle_client(client_socket, client_address):
    global session_data, socket_map
    
    session_id = recv_message(client_socket)
    client_id = recv_message(client_socket)

    print(f"Connection {client_address}, Session ID: {session_id}, Client ID: {client_id}")

    with session_lock:
        session_data.setdefault(session_id, []).append(client_id)

    with socket_lock:
        socket_map[client_id] = client_socket

    try:
        while True:
            message = recv_message(client_socket)
            if not message:
                break

            print(f"{client_id} says: {message}")

            # Broadcast message
            with session_lock:
                recipients = list(session_data.get(session_id, []))

            for other_client in recipients:
                if other_client != client_id:
                    try:
                        with socket_lock:
                            send_message(socket_map[other_client], f"{client_id}: {message}")
                    except:
                        # Remove disconnected clients during messaging
                        with socket_lock:
                            socket_map.pop(other_client, None)
                        with session_lock:
                            if other_client in session_data.get(session_id, []):
                                session_data[session_id].remove(other_client)

    finally:
        print(f"Connection with {client_address} has ended.")

        # Cleanup on exit
        with socket_lock:
            socket_map.pop(client_id, None)

        with session_lock:
            if client_id in session_data.get(session_id, []):
                session_data[session_id].remove(client_id)
            if not session_data.get(session_id): # if empty or missing
                session_data.pop(session_id, None)

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
