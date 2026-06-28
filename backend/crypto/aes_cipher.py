from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

NONCE_SIZE = 12

def encrypt(plaintext: bytes, key: bytes):

    nonce = get_random_bytes(NONCE_SIZE)

    cipher = AES.new(
        key,
        AES.MODE_GCM,
        nonce=nonce
    )

    ciphertext, tag = cipher.encrypt_and_digest(plaintext)

    return nonce, ciphertext, tag

def decrypt(
    nonce: bytes,
    ciphertext: bytes,
    tag: bytes,
    key: bytes,
):
    
    cipher = AES.new(
        key,
        AES.MODE_GCM,
        nonce=nonce
    )

    plaintext = cipher.decrypt_and_verify(
        ciphertext,
        tag
    )

    return plaintext