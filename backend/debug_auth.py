
from app.auth.jwt import create_access_token
from app.core.config import settings
from jose import jwt
from datetime import timedelta

print(f"SECRET_KEY: {settings.SECRET_KEY[:5]}...")
print(f"ALGORITHM: {settings.ALGORITHM}")

# 1. Create Token
email = "admin@example.com"
data = {"sub": email}
token = create_access_token(data, expires_delta=timedelta(minutes=15))
print(f"\nGenerated Token: {token}")

# 2. Decode Token same way dependencies.py does
try:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    print(f"\nDecoded Payload: {payload}")
    decoded_email = payload.get("sub")
    if decoded_email == email:
        print("\nSUCCESS: Email matches.")
    else:
        print(f"\nFAILURE: Email mismatch. Got {decoded_email}")
except Exception as e:
    print(f"\nFAILURE: Decoding raised exception: {e}")
