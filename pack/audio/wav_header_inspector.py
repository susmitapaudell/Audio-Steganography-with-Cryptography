"""
WAV Header Inspector
---------------------
Reads the first 44 bytes (standard PCM WAV header) of a .wav file and
prints every field individually: raw bytes (hex), interpreted value,
and what it means.

Usage:
    python wav_header_inspector.py path/to/file.wav
"""

import sys
import struct
import os


def read_wav_file(filepath):
    with open(filepath, "rb") as f:
        header = f.read(44)

    if len(header) < 44:
        raise ValueError(
            f"File is only {len(header)} bytes — too short to contain a standard 44-byte WAV header."
        )

    return {
        # ---------- RIFF CHUNK (bytes 0-11) ----------
        "chunk_id": header[0:4],  # raw bytes
        "chunk_size": struct.unpack('<I', header[4:8])[0],  
        "format_tag": header[8:12],

        # ---------- fmt SUBCHUNK (bytes 12-35) ----------
        "sub_chunk_id": header[12:16],
        "sub_chunk_size": struct.unpack('<I', header[16:20])[0], #unsigned 32 bit integer, little-endian
        "audio_format": struct.unpack('<H', header[20:22])[0],   #unsigned 16 bit integer, little-endian
        "num_channels": struct.unpack('<H', header[22:24])[0],
        "sample_rate": struct.unpack('<I', header[24:28])[0],
        "byte_rate": struct.unpack('<I', header[28:32])[0],
        "block_align": struct.unpack('<H', header[32:34])[0],
        "bits_per_sample": struct.unpack('<H', header[34:36])[0],

        # ---------- data SUBCHUNK (bytes 36-43) ----------
        "data_chunk_id": header[36:40],
        "data_chunk_size": struct.unpack('<I', header[40:44])[0],
    }


def info_wav_header(filepath):
    wav = read_wav_file(filepath)

    print(f"WAV HEADER INFORMATION: {filepath}")

    print("\n--- RIFF CHUNK (bytes 0-11) ---")
    print(f"[0:4]   ChunkID        : {wav['chunk_id']}")
    print(f"[4:8]   ChunkSize      : {wav['chunk_size']}")
    print(f"[8:12]  Format         : {wav['format_tag']}")

    print("\n--- fmt CHUNK (bytes 12-35) ---")
    print(f"[12:16] Subchunk1ID    : {wav['subchunk1_id']}")
    print(f"[16:20] Subchunk1Size  : {wav['subchunk1_size']}")
    print(f"[20:22] AudioFormat    : {wav['audio_format']}")
    print(f"[22:24] NumChannels    : {wav['num_channels']}")
    print(f"[24:28] SampleRate     : {wav['sample_rate']}")
    print(f"[28:32] ByteRate       : {wav['byte_rate']}")
    print(f"[32:34] BlockAlign     : {wav['block_align']}")
    print(f"[34:36] BitsPerSample  : {wav['bits_per_sample']}")

    print("\n--- data CHUNK HEADER (bytes 36-43) ---")
    print(f"[36:40] DatachunkID    : {wav['data_chunk_id']}")
    print(f"[40:44] DatachunkSize  : {wav['data_chunk_size']}")


def check_wav_compatibility(filepath):
    wav = read_wav_file(filepath)

    fmt_lookup = {1: "PCM", 3: "IEEE Float", 6: "A-law", 7: "Mu-law", 0xFFFE: "Extensible"}

    issues = []

    if wav['chunk_id'] != b'RIFF':
        issues.append("Not a RIFF file")
    if wav['format_tag'] != b'WAVE':
        issues.append("Not a WAVE format file")
    if wav['sub_chunk_id'] != b'fmt ':
        issues.append("fmt chunk not found at expected offset (file may have extra chunks before fmt)")

    # --- SubchunkSize check (fmt chunk payload size) ---
    if wav['sub_chunk_size'] != 16:
        issues.append(
            f"SubchunkSize is {wav['sub_chunk_size']}, expected 16 for standard PCM "
            f"(18 or 40 usually means extensible/float WAV) — convert with ffmpeg"
        )

    if wav['audio_format'] != 1:
        issues.append(
            f"AudioFormat is {fmt_lookup.get(wav['audio_format'], wav['audio_format'])}, "
            f"not PCM — convert with ffmpeg"
        )
    if wav['num_channels'] != 1:
        issues.append(f"NumChannels is {wav['num_channels']}, project requires MONO (1) — convert with ffmpeg (-ac 1)")
    if wav['bits_per_sample'] != 16:
        issues.append(f"BitsPerSample is {wav['bits_per_sample']}, not 16 — convert with ffmpeg")
    if wav['sample_rate'] not in (16000, 44100):
        issues.append(f"SampleRate is {wav['sample_rate']}, expected 16000 or 44100 — resample with ffmpeg")
    if wav['data_chunk_id'] != b'data':
        issues.append(
            "data chunk not found at byte 36 — file likely has extra metadata chunks "
            "(LIST/INFO/etc.) before data; do not hardcode offset 44 when reading samples"
        )

    # --- Data Chunk Size check
    actual_file_size = os.path.getsize(filepath)
    expected_file_size = wav['data_chunk_size'] + 44  # 44-byte header + declared data size
    if actual_file_size != expected_file_size:
        issues.append(
            f"Subchunk2Size mismatch: header declares {wav['data_chunk_size']} bytes of audio data "
            f"(implying file size {expected_file_size}), but actual file size on disk is "
            f"{actual_file_size} bytes — file may be truncated, corrupted, or have extra chunks after data"
        )

    # --- BlockAlign / ByteRate consistency check, useful alongside size checks ---
    expected_byte_rate = wav['sample_rate'] * wav['num_channels'] * wav['bits_per_sample'] // 8
    expected_block_align = wav['num_channels'] * wav['bits_per_sample'] // 8
    if expected_byte_rate != wav['byte_rate']:
        issues.append(f"ByteRate mismatch: header says {wav['byte_rate']}, expected {expected_byte_rate}")
    if expected_block_align != wav['block_align']:
        issues.append(f"BlockAlign mismatch: header says {wav['block_align']}, expected {expected_block_align}")

    print(f"\nCOMPATIBILITY CHECK: {filepath}")
    if issues:
        print("NOT READY for embedding. Issues found:")
        for i in issues:
            print(f"  - {i}")
    else:
        print("READY — file is mono, 16-bit PCM WAV at a supported sample rate.")

    return len(issues) == 0


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage:")
        print("  python3 wav_header_inspector.py <audio_file> --info")
        print("  python3 wav_header_inspector.py <audio_file> --comp")
        sys.exit(1)

    base_folder = "../../samples"

    filename = sys.argv[1]
    option = sys.argv[2]

    file_path = os.path.join(base_folder, filename)

    if not os.path.isfile(file_path):
        print(f"File '{filename}' not found.")
        sys.exit(1)

    if option == "--info":
        info_wav_header(file_path)

    elif option == "--comp":
        check_wav_compatibility(file_path)

    else:
        print(f"Unknown option: {option}")
        print("Valid options are:")
        print("  --info   Display WAV header information")
        print("  --comp   Check WAV compatibility")
        sys.exit(1)
