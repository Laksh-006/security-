from cryptography.fernet import Fernet
import os

def generate_key():
    return Fernet.generate_key()

def encrypt_file_data(data: bytes, key: bytes) -> bytes:
    f = Fernet(key)
    return f.encrypt(data)

def decrypt_file_data(encrypted_data: bytes, key: bytes) -> bytes:
    f = Fernet(key)
    return f.decrypt(encrypted_data)
