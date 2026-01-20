
from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib

class CredentialEncryptor:
    def __init__(self):
        # Ensure we have a valid 32-byte base64 key for Fernet
        # In prod, this should be settings.ENCRYPTION_KEY
        # For dev, we can derive it from SECRET_KEY if ENCRYPTION_KEY is missing
        key = getattr(settings, "ENCRYPTION_KEY", None)
        
        if not key:
            # Fallback: Derive a key from SECRET_KEY
            # Fernet requires a 32-byte URL-safe base64-encoded key
            kdf = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
            key = base64.urlsafe_b64encode(kdf)
            
        self.fernet = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypts a plaintext string."""
        if not plaintext:
            return None
        return self.fernet.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypts a ciphertext string."""
        if not ciphertext:
            return None
        return self.fernet.decrypt(ciphertext.encode()).decode()

encryptor = CredentialEncryptor()
