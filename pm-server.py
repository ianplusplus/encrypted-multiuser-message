import socket
import threading

session_data = {}
client_queue = {}

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
    global client_queue
    print(f"Connection from {client_address}")
    data = client_socket.recv(1024).decode()

    lines = data.split("\n")

    session_id = lines[0]
    client_id = lines[1]

    print(f"Session ID: {session_id}")
    print(f"Client ID: {client_id}")

    if session_id not in session_data:
        session_data[session_id] = []
    session_data[session_id].append(client_id)

    if client_id not in client_queue:
        client_queue[client_id] = []

    client_input = ""

    end = False

    while client_input != end:
        try:
            data = recv_message(client_socket)
            if not data:
                break
            print(f"\nReceived: ({client_id})", data)
            if client_input != ":end":
                for client in session_data[session_id]:
                    client_queue[client].append(client_input)
                for message in client_queue[client_id]:
                    send_message(client_socket, message)
                client_queue[client_id] = []
            else:
                end = True
        except:
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
