import socket
import threading
import argparse
from messages import recv_message, send_message, recv_message_raw
from akey import verify_message

# -------------------------------
# Global session and socket maps
# -------------------------------
session_data = {}  # {session_id: [client_id, ...]}
socket_map = {}    # {client_id: socket}
public_key_map = {}
client_verified = {}

session_lock = threading.Lock()
socket_lock = threading.Lock()
public_key_lock = threading.Lock()
client_verified_lock = threading.Lock()

# -------------------------------
# Helper functions for vouch system
# -------------------------------

def register_client(session_id, client_id, public_key):
    with client_verified_lock:
        if session_id not in client_verified:
            client_verified[session_id] = {}
        client_verified[session_id][client_id] = {
            "public_key": public_key,
            "vouched_by": set()
        }

def vouch_client(session_id, target_client_id, vouched_by_client_id):
    with client_verified_lock:
        try:
            client_verified[session_id][target_client_id]["vouched_by"].add(vouched_by_client_id)
        except KeyError:
            print("Session or target client not found")

def is_vouched(session_id, client_id):
    with client_verified_lock:
        try:
            return len(client_verified[session_id][client_id]["vouched_by"]) > 0
        except KeyError:
            return False
        
def get_verified_public_key(session_id, client_id) -> bytes | None:
    """
    Retrieve the public key of a client in a session.
    Returns None if the session or client is not registered.
    Thread-safe.
    """
    with client_verified_lock:
        try:
            return client_verified[session_id][client_id]["public_key"]
        except KeyError:
            return None


# -------------------------------
# Helper functions for public key storage
# -------------------------------

def set_public_key(client_id: str, session_id: str, public_key: bytes):
    if client_id not in public_key_map:
        public_key_map[client_id] = {}
    public_key_map[client_id][session_id] = public_key
    print(f"Public key for {client_id} added for session: {session_id}")


def get_public_key(client_id: str, session_id: str) -> bytes | None:
    return public_key_map.get(client_id, {}).get(session_id)


# -------------------------------
# Client handler
# -------------------------------
def handle_client(client_socket, client_address):
    try:
        # Receive session and client ID
        session_id = recv_message(client_socket)
        client_id = recv_message(client_socket)
        client_id_public_key = recv_message_raw(client_socket)

        print(f"Connection {client_address}, Session ID: {session_id}, Client ID: {client_id}")

        # -------------------------------
        # Remove stale socket if reconnecting
        # -------------------------------
        with socket_lock:
            old_socket = socket_map.get(client_id)
            if old_socket:
                try:
                    old_socket.close()
                except:
                    pass
                del socket_map[client_id]

        # -------------------------------
        # Add client to session
        # -------------------------------
        with session_lock:
            if session_id not in session_data:
                session_data[session_id] = []
            if client_id not in session_data[session_id]:
                session_data[session_id].append(client_id)

        # Register new socket
        with socket_lock:
            socket_map[client_id] = client_socket

        with public_key_lock:
            set_public_key(client_id, session_id, client_id_public_key)

        register_client(session_id, client_id, client_id_public_key)

        key_matches_id = client_id_public_key == get_verified_public_key(session_id, client_id)

        # -------------------------------
        # Message loop
        # -------------------------------
        while True:
            message = recv_message(client_socket)
            sig = recv_message(client_socket)

            if not verify_message(get_public_key(client_id, session_id), message, sig):
                message = None

            if not message:
                break

            print(f"{client_id} says: {message} Vouched: {is_vouched(session_id, client_id)}")   

            # Broadcast to all other clients in the same session
            with session_lock:
                recipients = session_data.get(session_id, []).copy()

            for other_client in recipients:
                if other_client == client_id:
                    continue
                with socket_lock:
                    sock = socket_map.get(other_client)
                if sock:
                    try:
                        send_message(sock, f"{client_id}: {message}")
                    except:
                        # Remove disconnected clients during broadcast
                        with socket_lock:
                            socket_map.pop(other_client, None)
                        with session_lock:
                            if other_client in session_data.get(session_id, []):
                                session_data[session_id].remove(other_client)

    except Exception as e:
        print(f"Error with client {client_id} ({client_address}): {e}")

    finally:
        # -------------------------------
        # Cleanup on disconnect
        # -------------------------------
        print(f"Connection with {client_address} ended.")

        with socket_lock:
            socket_map.pop(client_id, None)

        with session_lock:
            if client_id in session_data.get(session_id, []):
                session_data[session_id].remove(client_id)
            if not session_data.get(session_id):
                session_data.pop(session_id, None)

        try:
            client_socket.close()
        except:
            pass

# -------------------------------
# Server setup
# -------------------------------
parser = argparse.ArgumentParser(description="Port-Message Server")
parser.add_argument("--port", "-p", type=int, default=6767, help="Listening port for server.")
args = parser.parse_args()
port = args.port

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("0.0.0.0", port))
server_socket.listen(5)
server_socket.settimeout(1.0)
print(f"Server listening on port {port}...")

running = True

# -------------------------------
# Command listener for shutdown
# -------------------------------
def command_listener():
    global running
    while running:
        cmd = input()
        if cmd.lower() == ":end":
            running = False
            print("Stopping server...")
            try:
                server_socket.close()
            except:
                pass

threading.Thread(target=command_listener, daemon=True).start()

# -------------------------------
# Main accept loop
# -------------------------------
while running:
    try:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()
    except socket.timeout:
        # Accept timed out, check running again
        continue
    except OSError:
        # Socket closed during shutdown
        break
    except Exception as e:
        print(f"Error accepting connections: {e}")
