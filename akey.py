import subprocess
import os
import getpass
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

def generate_encrypted_ed25519_keypair(
    private_key_path="client_private_ed25519.pem",
    public_key_path="client_public_ed25519.pem"
):
    passphrase = getpass.getpass("Enter passphrase to encrypt private key: ")

    # Generate encrypted Ed25519 private key
    subprocess.run([
        "openssl", "genpkey",
        "-algorithm", "Ed25519",
        "-aes-256-cbc",
        "-pass", f"pass:{passphrase}",
        "-out", private_key_path
    ], check=True)

    # Extract public key
    subprocess.run([
        "openssl", "pkey",
        "-in", private_key_path,
        "-passin", f"pass:{passphrase}",
        "-pubout",
        "-out", public_key_path
    ], check=True)

    os.chmod(private_key_path, 0o600)
    print(f"Encrypted Ed25519 keypair created: {private_key_path} & {public_key_path}")

def load_private_key(private_path="client_private.pem"):
    with open(private_path, "rb") as key_file:
        encrypted_key = key_file.read()
    
    passphrase = getpass.getpass("Enter private key passphrase: ")

    private_key = serialization.load_pem_private_key(
        encrypted_key,
        password=passphrase.encode("utf-8")
    )
    print(f"Private key loaded: {private_path}")
    return private_key

def load_public_key(public_path="client_public.pem"):
    with open(public_path, "rb") as key_file:
        public_key_data = key_file.read()
    print(f"Public key loaded: {public_path}")
    return public_key_data  # we return raw PEM bytes here

def file_exists(path):
    if os.path.exists(path):
        return True
    else:
        return False
    
def sign_message(private_key, message_bytes: bytes) -> bytes:
    """
    Signs a message using the provided Ed25519 private key.
    Returns the signature bytes.
    """
    signature = private_key.sign(message_bytes)
    return signature

def verify_message(public_key_pem: bytes, message: bytes, signature: bytes) -> bool:
    """
    Returns True if the signature is valid, False otherwise.
    """
    public_key = serialization.load_pem_public_key(public_key_pem)
    try:
        public_key.verify(signature, message)
        return True
    except Exception:
        return False