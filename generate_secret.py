import secrets

# Generate a 32-byte random secret key
new_secret = secrets.token_hex(32)
print(new_secret)
