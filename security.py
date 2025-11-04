from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import base64

def encrypt(plaintext: str, password: str) -> str:
    plaintext_bytes = plaintext.encode()
    password_bytes = password.encode()

    # Generate random salt and IV
    salt = os.urandom(16)
    iv = os.urandom(16)

    # Derive key from password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(password_bytes)

    # Pad plaintext
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plaintext_bytes) + padder.finalize()

    # Encrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()

    # Combine salt + iv + ciphertext and encode as base64
    encrypted_message = base64.b64encode(salt + iv + ciphertext).decode()
    return encrypted_message

def decrypt(encrypted_message: str, password: str) -> str:
    password_bytes = password.encode()
    decoded = base64.b64decode(encrypted_message)

    # Extract salt, iv, and ciphertext
    salt = decoded[:16]
    iv = decoded[16:32]
    ciphertext = decoded[32:]

    # Derive key from password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000,
        backend=default_backend()
    )
    key = kdf.derive(password_bytes)

    # Decrypt
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

    # Unpad
    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
    return decrypted.decode()

