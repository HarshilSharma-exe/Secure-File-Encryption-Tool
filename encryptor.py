
import os
import sys
import getpass
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# Folders
BASE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(BASE, "input")
CIPHER = os.path.join(BASE, "ciphertext")
OUTPUT = os.path.join(BASE, "output")


# Make a key from password and salt
def make_key(password, salt):
    if not password:
        raise ValueError("Password cannot be empty.")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000
    )
    return kdf.derive(password.encode())


# Encrypt a file
def encrypt_file(source, destination, password):
    with open(source, "rb") as f:
        data = f.read()

    if not data:
        raise ValueError("File is empty.")

    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = make_key(password, salt)

    encrypted = AESGCM(key).encrypt(nonce, data, None)

    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with open(destination, "wb") as f:
        f.write(salt + nonce + encrypted)


# Decrypt a file
def decrypt_file(source, destination, password):
    with open(source, "rb") as f:
        data = f.read()

    if len(data) < 44:
        raise ValueError("Invalid encrypted file.")

    salt = data[:16]
    nonce = data[16:28]
    encrypted = data[28:]

    key = make_key(password, salt)

    try:
        original = AESGCM(key).decrypt(nonce, encrypted, None)
    except InvalidTag:
        raise ValueError("Wrong password or file changed.")

    os.makedirs(os.path.dirname(destination), exist_ok=True)
    with open(destination, "wb") as f:
        f.write(original)


# Main program
def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("encrypt", "decrypt"):
        print("Use: python encryptor.py encrypt notes.txt")
        print("Or:  python encryptor.py decrypt notes.txt.enc")
        return

    command = sys.argv[1]
    name = os.path.basename(sys.argv[2])

    try:
        if command == "encrypt":
            source = os.path.join(INPUT, name)
            destination = os.path.join(CIPHER, name + ".enc")

            password = getpass.getpass("Enter password: ")
            again = getpass.getpass("Repeat password: ")

            if password != again:
                raise ValueError("Passwords do not match.")

            encrypt_file(source, destination, password)

        else:
            source = os.path.join(CIPHER, name)
            original_name = name[:-4] if name.endswith(".enc") else name + ".decrypted"
            destination = os.path.join(OUTPUT, original_name)

            password = getpass.getpass("Enter password: ")
            decrypt_file(source, destination, password)

        print("Done! Saved as:", destination)

    except (ValueError, OSError) as error:
        print("Error:", error)


if __name__ == "__main__":
    main()
