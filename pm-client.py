import socket
import argparse
from security import encrypt, decrypt
import threading

running = True

def send_message(sock, text):
    data = text.encode('utf-8')
    length = len(data).to_bytes(4, 'big')  # 4-byte length prefix
    sock.sendall(length + data)

def receive(sock):
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break
            print("\nReceived:", data)
        except:
            break

def send(sock):
    global running

    print("Enter in message. Press enter to send message. Send ':end' to end communication.")

    while True:

        user_input = input()
        if user_input != ":end":
            user_input = encrypt(user_input, password)
        else:
            running = False

        send_message(sock, user_input)

parser = argparse.ArgumentParser(description="Port-Message Client")

parser.add_argument("--address", "-a", help="Address of the server.")
parser.add_argument("--port", "-p", type=int, default=6767, help="Listening port for server.")
parser.add_argument("--secret", "-s", help="Sets the password.")
parser.add_argument("--id", "-i", help="Session ID for the communication.")
parser.add_argument("--name", "-n", help="Client unique identifier.")
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
    sessionid = input("Enter the session id: ")
else:
    sessionid = args.id

if args.name == None:
    clientname = input("Enter the unique name: ")
else:
    clientname = args.name

client_socket.sendall((sessionid + "\n").encode())
client_socket.sendall((clientname + "\n").encode())

threading.Thread(target=receive, args=(client_socket,), daemon=True).start()
threading.Thread(target=send, args=(client_socket,), daemon=True).start()

while running:
    pass

client_socket.close()


# Keep main thread alive




#need to add logic to the server to send back messages to the clients, currently the messages
# are just being logged on the server under their session id