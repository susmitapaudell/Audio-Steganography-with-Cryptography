from stegano.wav_io import load_wav, save_wav
from stegano.dsss_codec import embed_bytes, extract_bytes
from stegano.metrices import calculate_all_metrics

from crypto import serializer
from crypto import key_derivation
from crypto import aes_cipher
from crypto import envelop


INPUT_WAV = (
    "/Users/susmitapaudel/Projects/"
    "Audio-Steganography-with-Cryptography/"
    "backend/input-audio/file_example_WAV_5MG.wav"
)

OUTPUT_WAV = (
    "/Users/susmitapaudel/Projects/"
    "Audio-Steganography-with-Cryptography/"
    "backend/output-audio/output1.wav"
)

SEED = 12345

PASSWORD = "MyStrongPassword"


METADATA = {
    "author": "John Smith",
    "production": "Universal Studios",
    "copyright": "2026",
}


def main():

    # =========================================================
    # 1. LOAD ORIGINAL AUDIO
    # =========================================================

    audio, sample_rate = load_wav(INPUT_WAV)

    print("Original audio loaded.")
    print(f"Sample rate: {sample_rate} Hz")
    print(f"Samples: {len(audio)}")


    # =========================================================
    # 2. SERIALIZE METADATA
    # =========================================================

    json_string = serializer.metadata_to_json(
        METADATA
    )

    plaintext = json_string.encode("utf-8")

    print("\nOriginal metadata:")
    print(json_string)

    print(
        f"Plaintext size: {len(plaintext)} bytes"
    )


    # =========================================================
    # 3. GENERATE SALT
    # =========================================================

    salt = key_derivation.generate_salt()


    # =========================================================
    # 4. DERIVE AES-256 KEY
    # =========================================================

    key = key_derivation.derive_key(
        PASSWORD,
        salt,
    )

    print(
        f"\nDerived AES key: "
        f"{key.hex()}"
    )


    # =========================================================
    # 5. AES-256-GCM ENCRYPTION
    # =========================================================

    nonce, ciphertext, tag = aes_cipher.encrypt(
        plaintext,
        key,
    )

    print("\nAES-GCM encryption complete.")

    print(
        f"Nonce:      {len(nonce)} bytes"
    )

    print(
        f"Ciphertext: {len(ciphertext)} bytes"
    )

    print(
        f"Tag:        {len(tag)} bytes"
    )


    # =========================================================
    # 6. CREATE COMPLETE ENCRYPTED PAYLOAD
    #
    # The payload format is:
    #
    #     salt | nonce | ciphertext | tag
    #
    # envelop.pack() handles this.
    # =========================================================

    secret_bytes = envelop.pack(
        salt,
        nonce,
        ciphertext,
        tag,
    )

    print(
        f"\nTotal encrypted payload: "
        f"{len(secret_bytes)} bytes"
    )


    # =========================================================
    # 7. EMBED PAYLOAD USING DSSS
    # =========================================================

    stego = embed_bytes(
        audio,
        secret_bytes,
        seed=SEED,
    )

    print("\nDSSS embedding complete.")


    # =========================================================
    # 8. SAVE STEGO AUDIO
    # =========================================================

    save_wav(
        OUTPUT_WAV,
        stego,
        sample_rate,
    )

    print(
        f"Stego audio saved to:\n"
        f"{OUTPUT_WAV}"
    )


    # =========================================================
    # 9. EXTRACT PAYLOAD FROM STEGO AUDIO
    # =========================================================

    recovered_payload = extract_bytes(
        stego,
        seed=SEED,
    )

    print("\nDSSS extraction complete.")

    print(
        f"Recovered payload: "
        f"{len(recovered_payload)} bytes"
    )


    # =========================================================
    # 10. CALCULATE METRICS
    #
    # Compare the complete encrypted payload:
    #
    # original:
    #     salt + nonce + ciphertext + tag
    #
    # recovered:
    #     extracted salt + nonce + ciphertext + tag
    # =========================================================

    metrics = calculate_all_metrics(
        audio,
        stego,
        secret_bytes,
        recovered_payload,
    )


    print("\n" + "=" * 55)
    print("AUDIO QUALITY METRICS")
    print("=" * 55)

    print(
        f"SNR:         "
        f"{metrics['snr_db']:.2f} dB"
    )

    print(
        f"MSE:         "
        f"{metrics['mse']:.10f}"
    )

    print(
        f"RMSE:        "
        f"{metrics['rmse']:.10f}"
    )

    print(
        f"MAE:         "
        f"{metrics['mae']:.10f}"
    )

    print(
        f"PSNR:        "
        f"{metrics['psnr_db']:.2f} dB"
    )

    print(
        f"Correlation: "
        f"{metrics['correlation']:.8f}"
    )

    print(
        f"Clipping:    "
        f"{metrics['clipping_rate']:.8f}"
    )


    print("\n" + "=" * 55)
    print("DATA RECOVERY METRICS")
    print("=" * 55)

    print(
        f"BER: "
        f"{metrics['ber']:.8f}"
    )

    print(
        f"Payload identical: "
        f"{secret_bytes == recovered_payload}"
    )


    # =========================================================
    # 11. UNPACK RECOVERED PAYLOAD
    #
    # recovered_payload contains:
    #
    #     salt | nonce | ciphertext | tag
    #
    # envelop.unpack() separates them.
    # =========================================================

    (
        recovered_salt,
        recovered_nonce,
        recovered_ciphertext,
        recovered_tag,
    ) = envelop.unpack(
        recovered_payload
    )


    # =========================================================
    # 12. DERIVE KEY AGAIN
    #
    # We DO NOT store the AES key inside the audio.
    #
    # We recover the salt and use the password again to
    # derive the same 256-bit AES key.
    # =========================================================

    recovered_key = key_derivation.derive_key(
        PASSWORD,
        recovered_salt,
    )


    # =========================================================
    # 13. AES-GCM DECRYPTION
    # =========================================================

    try:

        recovered_plaintext = aes_cipher.decrypt(
            recovered_nonce,
            recovered_ciphertext,
            recovered_tag,
            recovered_key,
        )

        print(
            "\nAES-GCM authentication: SUCCESS"
        )

    except Exception as e:

        print(
            "\nAES-GCM authentication: FAILED"
        )

        print(
            f"Reason: {e}"
        )

        return


    # =========================================================
    # 14. DECODE UTF-8
    # =========================================================

    recovered_json = (
        recovered_plaintext.decode("utf-8")
    )


    # =========================================================
    # 15. DESERIALIZE JSON
    # =========================================================

    recovered_metadata = (
        serializer.json_to_metadata(
            recovered_json
        )
    )


    # =========================================================
    # 16. DISPLAY FINAL RESULT
    # =========================================================

    print("\n" + "=" * 55)
    print("RECOVERED METADATA")
    print("=" * 55)

    print(recovered_metadata)


    # =========================================================
    # 17. FINAL VERIFICATION
    # =========================================================

    print("\n" + "=" * 55)
    print("FINAL VERIFICATION")
    print("=" * 55)

    print(
        "Metadata identical:",
        METADATA == recovered_metadata,
    )

    print(
        "Payload identical:",
        secret_bytes == recovered_payload,
    )

    print(
        "Output:",
        OUTPUT_WAV,
    )


if __name__ == "__main__":
    main()