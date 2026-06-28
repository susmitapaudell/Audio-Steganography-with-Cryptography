from typing import Tuple

SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16


def pack(
    salt: bytes,
    nonce: bytes,
    ciphertext: bytes,
    tag: bytes,
) -> bytes:

    return salt + nonce + ciphertext + tag  #concatenates


def unpack(payload: bytes) -> Tuple[bytes, bytes, bytes, bytes]:

    salt = payload[:SALT_SIZE]

    nonce = payload[
        SALT_SIZE:
        SALT_SIZE + NONCE_SIZE
    ]

    tag = payload[-TAG_SIZE:]

    ciphertext = payload[
        SALT_SIZE + NONCE_SIZE:
        -TAG_SIZE
    ]

    return salt, nonce, ciphertext, tag