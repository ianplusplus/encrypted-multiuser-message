import socket

def send_message(sock, text):
    data = text.encode('utf-8')
    length = len(data).to_bytes(4, 'big')  # 4-byte length prefix
    sock.sendall(length + data)

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

def send_message_raw(sock, text):
    data = text
    length = len(data).to_bytes(4, 'big')  # 4-byte length prefix
    sock.sendall(length + data)

def recv_message_raw(sock):
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

    return data