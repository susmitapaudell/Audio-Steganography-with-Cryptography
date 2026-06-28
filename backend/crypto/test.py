#serialize
import serializer

metadata = {
    "author": "John Smith",
    "production": "Universal Studios",
    "copyright": "2026"
}

json_string = serializer.metadata_to_json(metadata)
plaintext = json_string.encode("utf-8")



#derive key
import key_derivation

password = "MyStrongPassword"

salt = key_derivation.generate_salt()

key = key_derivation.derive_key(password, salt)

print(key.hex())



#encrypt-decrypt
import aes_cipher

nonce, ciphertext, tag = aes_cipher.encrypt(plaintext, key)

print("Nonce:", nonce.hex())
print("Ciphertext:", ciphertext.hex())
print("Tag:", tag.hex())

# Decrypt
recovered = aes_cipher.decrypt(nonce, ciphertext, tag, key)

print(recovered.decode("utf-8"))