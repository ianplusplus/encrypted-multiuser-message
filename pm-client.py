import socket
import argparse
from security import encrypt, decrypt
import threading

running = True

def receive(sock):
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print("\nReceived:", data.decode())
        except:
            break

def send(sock):
    global running
    while True:
        print("Enter in messages. Press enter to send message. Send ':end' to end communication.")

        user_input = input()
        if user_input != ":end":
            user_input = encrypt(user_input, password)
        else:
            running = False

        while user_input != ":end":
            client_socket.sendall(user_input.encode())
            user_input = input()
            if user_input != ":end":
                user_input = encrypt(user_input, password)
            else:
                running = False
        client_socket.sendall(user_input.encode())

parser = argparse.ArgumentParser(description="Port-Message Client")

parser.add_argument("--address", "-a", help="Address of the server.")
parser.add_argument("--port", "-p", type=int, default=6767, help="Listening port for server.")
parser.add_argument("--secret", "-s", help="Sets the password")
parser.add_argument("--id", "-i", help="Session ID for the communication")
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

client_socket.sendall(sessionid.encode())

threading.Thread(target=receive, args=(client_socket,), daemon=True).start()
threading.Thread(target=send, args=(client_socket,), daemon=True).start()

while running:
    pass

client_socket.close()


# Keep main thread alive




#need to add logic to the server to send back messages to the clients, currently the messages
# are just being logged on the server under their session id