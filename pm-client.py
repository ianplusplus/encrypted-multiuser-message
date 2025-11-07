import socket
import argparse
from security import encrypt, decrypt
from messages import recv_message, send_message
from create-key import generate_encrypted_ed25519_keypair
import threading


running = True

def receive(sock, passwd):
    while True:
        try:
            data = recv_message(sock)
            if not data:
                break

            split_data = data.split(" ")
            plain_text = decrypt(split_data[1], passwd)

            print(f"{split_data[0]}", plain_text)
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
parser.add_argument("--key", "-k", help="Creates a key pair for the client/session combination.", action="store_true")
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

if args.key:
    generate_encrypted_ed25519_keypair(f"{clientname}.{sessionid}_private_ed25519.pem", f"{clientname}.{sessionid}_public_ed25519.pem")

send_message(client_socket, sessionid)
send_message(client_socket, clientname)

threading.Thread(target=receive, args=(client_socket, password), daemon=True).start()
threading.Thread(target=send, args=(client_socket,), daemon=True).start()

while running:
    pass

client_socket.close()


# Keep main thread alive




#need to add logic to the server to send back messages to the clients, currently the messages
# are just being logged on the server under their session id