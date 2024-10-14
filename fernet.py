from cryptography.fernet import Fernet

# Generate a new Fernet key
key = Fernet.generate_key()

# Save the key to a file for later use
with open("fernet_key.txt", "wb") as key_file:
    key_file.write(key)

print(f"Generated key: {key.decode()}")