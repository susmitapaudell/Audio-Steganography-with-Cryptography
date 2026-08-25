import numpy as np

HEADER_BITS = 32

def bytes_to_bits(data: bytes) -> np.ndarray:
    """Convert bytes to 0/1 bits."""
    return np.unpackbits(
        np.frombuffer(data, dtype=np.uint8)
    ).astype(np.int8)


def bits_to_bytes(bits: np.ndarray) -> bytes:
    """Convert 0/1 bits to bytes."""
    return np.packbits(bits.astype(np.uint8)).tobytes()


def make_frame(secret_bytes: bytes) -> np.ndarray:
    """Create [32-bit length][payload bits]."""
    payload_bits = bytes_to_bits(secret_bytes)

    # Header stores the payload length in bits.
    header_bits = np.array(
        [
            int(b)
            for b in format(len(payload_bits), f"0{HEADER_BITS}b")
        ],
        dtype=np.int8,
    )

    return np.concatenate([header_bits, payload_bits])


def frame_capacity_bits(total_bit_slots: int) -> int:
    """Return payload capacity after the header."""
    return max(0, total_bit_slots - HEADER_BITS)