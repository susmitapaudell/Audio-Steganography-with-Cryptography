from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes


SALT_SIZE = 16
KEY_SIZE = 32          # 32 bytes = 256 bits
ITERATIONS = 150000


def generate_salt() -> bytes:

    return get_random_bytes(SALT_SIZE)


def derive_key(password: str, salt: bytes) -> bytes:

    return PBKDF2(
        password,
        salt,
        dkLen=KEY_SIZE,
        count=ITERATIONS,
    )