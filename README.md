**serializer.py :** Metadata (Python Dictionary) -> JSON Serialization -> UTF-8 Encoding -> **key_derivation.py :** Password + Salt -> PBKDF2 Key Derivation -> 256-bit AES Key -> **aes_cipher** : AES-256-GCM Encryption -> Nonce + Ciphertext + Authentication Tag


# wav_header_inspector.py

## Usage

Run the script from the command line with one of the following options.

### Display WAV header information

```bash
python3 wav_header_inspector.py <audio_file> --info
```

Displays information extracted from the WAV file header.

### Run header comparison

```bash
python3 wav_header_inspector.py <audio_file> --comp
```

Runs the comparison functionality for the specified WAV file.
```