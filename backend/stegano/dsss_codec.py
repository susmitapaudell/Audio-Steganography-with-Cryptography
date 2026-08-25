import numpy as np

from .pn_sequence import generate_pn_sequence
from .frame import make_frame, bits_to_bytes, frame_capacity_bits, HEADER_BITS


DEFAULT_SPREADING_FACTOR = 384
DEFAULT_ALPHA_RATIO = 0.1
DEFAULT_FLAT_ALPHA = 0.08

FLAT_REFERENCE_RMS = 0.12
HEADER_STRENGTH_MULTIPLIER = 2.0
DEFAULT_REPETITION = 3

def capacity_bits(
    num_samples: int,
    spreading_factor: int = DEFAULT_SPREADING_FACTOR,
) -> int:
    """Return the number of payload bits the audio can hold."""

    # One slot contains spreading_factor samples.
    total_slots = num_samples // spreading_factor

    available_slots = total_slots - HEADER_BITS

    return available_slots // DEFAULT_REPETITION


def embed_bytes(
    audio: np.ndarray,
    secret_bytes: bytes,
    seed: int,
    spreading_factor: int = DEFAULT_SPREADING_FACTOR,
    mode: str = "adaptive",
    alpha_ratio: float = DEFAULT_ALPHA_RATIO,
    alpha: float = DEFAULT_FLAT_ALPHA,
) -> np.ndarray:
    """Embed encrypted bytes into audio using DSSS."""

    if mode not in ("adaptive", "flat"):
        raise ValueError("mode must be 'adaptive' or 'flat'")

    # Add the payload-length header.
    all_bits = make_frame(secret_bytes)
    n_payload = len(all_bits) - HEADER_BITS

    # Determine how many complete DSSS slots the audio has.
    total_slots = len(audio) // spreading_factor
    available = frame_capacity_bits(total_slots)

    if n_payload > available:
        raise ValueError(
            f"Audio too short: can hold {available} payload bits, "
            f"need {n_payload}. Use longer audio, a smaller message, "
            f"or a smaller spreading_factor."
        )

    # Spread payload bits across the available slots.
    slots_after_header = total_slots - HEADER_BITS
    stride = max(1, slots_after_header // max(1, n_payload))

    # Generate the same PN sequence used during extraction.
    pn = generate_pn_sequence(spreading_factor, seed)

    stego = audio.copy()

    def write_bit(slot_index: int, bit: int, boost: float = 1.0):
        """Embed one bit into one audio slot."""

        # Map bits to opposite PN polarities.
        symbol = 1.0 if bit == 1 else -1.0

        start = slot_index * spreading_factor
        end = start + spreading_factor

        if mode == "adaptive":
            segment = audio[start:end]

            # Stronger embedding is allowed in louder regions.
            local_rms = np.sqrt(np.mean(segment ** 2)) + 1e-6
            strength = alpha_ratio * local_rms

        else:
            local_rms = np.sqrt(
                np.mean(audio[start:end] ** 2)
            ) + 1e-6

            strength = alpha * min(
                1.0,
                local_rms / FLAT_REFERENCE_RMS,
            )

        # Add the spread bit signal to the existing audio samples.
        stego[start:end] += (strength * boost) * symbol * pn

    # Embed the header with extra protection.
    for i in range(HEADER_BITS):
        write_bit(
            i,
            all_bits[i],
            boost=HEADER_STRENGTH_MULTIPLIER,
        )

    # Embed payload bits across the remaining slots.
    for i in range(n_payload):

        bit = all_bits[HEADER_BITS + i]

        for repetition in range(DEFAULT_REPETITION):

            slot_index = (
                HEADER_BITS
                + i * DEFAULT_REPETITION
                + repetition
            )

            write_bit(
                slot_index,
                bit,
            )
    return np.clip(stego, -1.0, 1.0)


def extract_bytes(
    stego_audio: np.ndarray,
    seed: int,
    spreading_factor: int = DEFAULT_SPREADING_FACTOR,
) -> bytes:
    """Extract encrypted bytes from DSSS stego audio."""

    # Regenerate the PN sequence using the same seed.
    pn = generate_pn_sequence(spreading_factor, seed)

    total_slots = len(stego_audio) // spreading_factor

    def decode_bit(slot_index: int) -> int:

        start = slot_index * spreading_factor
        end = start + spreading_factor

        segment = stego_audio[start:end]

        segment = segment - np.mean(segment)
        pn_centered = pn - np.mean(pn)

        denominator = (
            np.linalg.norm(segment)
            * np.linalg.norm(pn_centered)
        )

        if denominator == 0:
            return 0

        corr = np.dot(segment, pn_centered) / denominator

        return 1 if corr > 0 else 0

    # Recover the 32-bit payload-length header.
    header_bits = np.array(
        [decode_bit(i) for i in range(HEADER_BITS)],
        dtype=np.int8,
    )

    # Convert binary header to payload length.
    n_payload = int(
        "".join(str(b) for b in header_bits),
        2,
    )

    slots_after_header = total_slots - HEADER_BITS

    if n_payload < 0 or n_payload > slots_after_header:
        raise ValueError(
            f"Header decoded to an implausible payload length "
            f"({n_payload} bits). This usually means the wrong "
            f"seed/spreading_factor was used, or the header was "
            f"corrupted."
        )

    # Reproduce the same payload spacing used during embedding.
    stride = max(
        1,
        slots_after_header // max(1, n_payload),
    )

    # Recover each payload bit through correlation.
    
        # Recover each payload bit through correlation.

    payload_bits = []

    for i in range(n_payload):

        votes = []

        for repetition in range(DEFAULT_REPETITION):

            slot_index = (
                HEADER_BITS
                + i * DEFAULT_REPETITION
                + repetition
            )

            votes.append(
                decode_bit(slot_index)
            )

        bit = int(
            sum(votes) >= (DEFAULT_REPETITION / 2)
        )

        payload_bits.append(bit)

    # IMPORTANT:
    # This must be OUTSIDE the for loop.
    payload_bits = np.array(
        payload_bits,
        dtype=np.int8,
    )

    return bits_to_bytes(payload_bits)