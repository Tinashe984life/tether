import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_SIZE = 12

def encrypt_text(plaintext: str, key_hex: str) -> str:
    if plaintext is None:
        return None
    key = bytes.fromhex(key_hex)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ct = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return nonce.hex() + ct.hex()

def decrypt_text(encrypted_hex: str, key_hex: str) -> str:
    if encrypted_hex is None:
        return None
    key = bytes.fromhex(key_hex)
    nonce = bytes.fromhex(encrypted_hex[:NONCE_SIZE*2])
    ct = bytes.fromhex(encrypted_hex[NONCE_SIZE*2:])
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ct, None)
    return pt.decode('utf-8')
