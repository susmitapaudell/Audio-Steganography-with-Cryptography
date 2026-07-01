**serializer.py :** Metadata (Python Dictionary) -> JSON Serialization -> UTF-8 Encoding -> **key_derivation.py :** Password + Salt -> PBKDF2 Key Derivation -> 256-bit AES Key -> **aes_cipher** : AES-256-GCM Encryption -> Nonce + Ciphertext + Authentication Tag


# wav_header_inspector.py


Run the script from the command line with one of the following options. The system argument takes file from samples folder. No need mention it in the path while giving argument.


### Display WAV header information

```bash
python3 wav_header_inspector.py <audio_file> --info
```

Displays if wav file is compatible for our project based on the header.

### Run header compatibility

```bash
python3 wav_header_inspector.py <audio_file> --comp
```

Runs the comparison functionality for the specified WAV file.
```