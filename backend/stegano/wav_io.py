import numpy as np
import soundfile as sf


def load_wav(path: str):
    """Load WAV as float64 samples in [-1, 1]."""
    audio, sample_rate = sf.read(path, dtype="float64")

    # Downmix stereo to mono.
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    return audio, sample_rate


def save_wav(path: str, audio: np.ndarray, sample_rate: int):
    """Save audio as 16-bit PCM WAV."""
    audio = np.clip(audio, -1.0, 1.0)
    sf.write(path, audio, sample_rate, subtype="PCM_16")