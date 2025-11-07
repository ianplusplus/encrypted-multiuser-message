import subprocess
import os
import getpass

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
