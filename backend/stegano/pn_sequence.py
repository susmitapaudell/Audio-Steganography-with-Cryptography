import numpy as np
from scipy.signal import butter, filtfilt


def generate_pn_sequence(
    length: int,
    seed: int,
    sample_rate: int = 44100,
    cutoff_hz: int = 10000,
) -> np.ndarray:
    """Generate a deterministic PN sequence."""

    # Same seed produces the same sequence.
    rng = np.random.RandomState(seed)
    raw = rng.choice([-1, 1], size=length).astype(np.float64)

    if length < 15:
        return raw

    nyquist = sample_rate / 2

    # Limit the PN sequence bandwidth.
    b, a = butter(4, cutoff_hz / nyquist, btype="low")
    shaped = filtfilt(b, a, raw)

    # Normalize amplitude.
    return shaped / (np.std(shaped) + 1e-9)