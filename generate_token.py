import secrets

token = secrets.token_urlsafe(32)  # Generates a 32-byte (256-bit) URL-safe token
print(token)