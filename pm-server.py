import socket
import threading

session_data = {}
socket_map = {}

def recv_message(sock):
    # Receive the 4-byte size prefix
    length_bytes = sock.recv(4)
    if not length_bytes:
        return None

    length = int.from_bytes(length_bytes, 'big')

    # Read exact number of bytes
    data = b''
    while len(data) < length:
        packet = sock.recv(length - len(data))
        if not packet:
            return None
        data += packet

    return data.decode('utf-8')

def send_message(sock, text):
    data = text.encode('utf-8')
    length = len(data).to_bytes(4, 'big')  # 4-byte length prefix
    sock.sendall(length + data)


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
                    send_message(socket_map[other_client], "{client_id}: {message}")

        except Exception as e:
            print("Error:", e)
            break

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
