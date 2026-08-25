"""
Quality metrics for evaluating stego audio.

Audio-quality metrics:
    - SNR
    - MSE
    - RMSE
    - PSNR
    - Pearson correlation
    - MAE
    - Clipping rate

Data-recovery metric:
    - Bit Error Rate (BER)
"""

import numpy as np

from .frame import bytes_to_bits


def _match_length(
    original: np.ndarray,
    stego: np.ndarray,
):
    """
    Match both audio arrays to the same length.
    """

    n = min(len(original), len(stego))

    return original[:n], stego[:n]


def mse(
    original: np.ndarray,
    stego: np.ndarray,
) -> float:
    """
    Calculate Mean Squared Error between
    original and stego audio.

    Lower MSE means less embedding distortion.
    """

    original, stego = _match_length(original, stego)

    error = stego - original

    return float(np.mean(error ** 2))


def rmse(
    original: np.ndarray,
    stego: np.ndarray,
) -> float:
    """
    Calculate Root Mean Squared Error.

    RMSE is in the same amplitude scale as the audio.
    Lower is better.
    """

    return float(np.sqrt(mse(original, stego)))


def mae(
    original: np.ndarray,
    stego: np.ndarray,
) -> float:
    """
    Calculate Mean Absolute Error.

    Lower MAE means less average sample-level distortion.
    """

    original, stego = _match_length(original, stego)

    error = np.abs(stego - original)

    return float(np.mean(error))


def snr_db(
    original: np.ndarray,
    stego: np.ndarray,
) -> float:
    """
    Calculate Signal-to-Noise Ratio in dB.

    Here, the difference between the original and stego
    audio is treated as embedding noise.

    Higher SNR is better.
    """

    original, stego = _match_length(original, stego)

    noise = stego - original

    signal_power = np.mean(original ** 2)
    noise_power = np.mean(noise ** 2)

    if noise_power == 0:
        return float("inf")

    if signal_power == 0:
        return float("-inf")

    return float(
        10 * np.log10(signal_power / noise_power)
    )


def psnr_db(
    original: np.ndarray,
    stego: np.ndarray,
    max_value: float = 1.0,
) -> float:
    """
    Calculate Peak Signal-to-Noise Ratio in dB.

    Assumes audio is normalized to [-1, 1]
    by default.

    Higher PSNR is better.
    """

    error = mse(original, stego)

    if error == 0:
        return float("inf")

    return float(
        10 * np.log10((max_value ** 2) / error)
    )


def correlation_coefficient(
    original: np.ndarray,
    stego: np.ndarray,
) -> float:
    """
    Calculate Pearson correlation coefficient
    between original and stego audio.

    A value close to 1 means the two waveforms
    are highly similar.
    """

    original, stego = _match_length(original, stego)

    if np.std(original) == 0 or np.std(stego) == 0:
        return 0.0

    correlation = np.corrcoef(
        original,
        stego,
    )[0, 1]

    return float(correlation)


def bit_error_rate(
    original_bytes: bytes,
    recovered_bytes: bytes,
) -> float:
    """
    Calculate Bit Error Rate (BER).

    BER = number of incorrect bits /
          total number of compared bits.

    Lower BER is better.
    """

    original_bits = bytes_to_bits(original_bytes)
    recovered_bits = bytes_to_bits(recovered_bytes)

    if len(original_bits) == 0:
        return (
            0.0
            if len(recovered_bits) == 0
            else 1.0
        )

    max_length = max(
        len(original_bits),
        len(recovered_bits),
    )

    errors = 0

    for i in range(max_length):

        if i >= len(original_bits):
            errors += 1
            continue

        if i >= len(recovered_bits):
            errors += 1
            continue

        if original_bits[i] != recovered_bits[i]:
            errors += 1

    return float(errors) / max_length


def clipping_rate(
    audio: np.ndarray,
) -> float:
    """
    Calculate the fraction of samples outside
    the valid normalized audio range [-1, 1].

    This should ideally be calculated on the
    un-clipped stego signal, before np.clip().

    Lower is better; ideally 0.
    """

    if len(audio) == 0:
        return 0.0

    clipped = np.sum(
        (audio < -1.0) | (audio > 1.0)
    )

    return float(clipped) / len(audio)


def calculate_all_metrics(
    original: np.ndarray,
    stego: np.ndarray,
    original_bytes: bytes | None = None,
    recovered_bytes: bytes | None = None,
) -> dict:
    """
    Calculate all available audio-quality metrics.

    BER is calculated only if original_bytes and
    recovered_bytes are provided.
    """

    metrics = {
        "snr_db": snr_db(original, stego),
        "mse": mse(original, stego),
        "rmse": rmse(original, stego),
        "mae": mae(original, stego),
        "psnr_db": psnr_db(original, stego),
        "correlation": correlation_coefficient(
            original,
            stego,
        ),
        "clipping_rate": clipping_rate(stego),
    }

    if (
        original_bytes is not None
        and recovered_bytes is not None
    ):
        metrics["ber"] = bit_error_rate(
            original_bytes,
            recovered_bytes,
        )

    return metrics