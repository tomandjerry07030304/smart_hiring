"""
Encryption Manager for Sensitive Data
Handles encryption/decryption of PII and sensitive fields
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """Manages encryption/decryption of sensitive data"""
    
    def __init__(self):
        """Initialize encryption manager"""
        self._fernet = None
        self._initialize_key()
    
    def _initialize_key(self):
        """Initialize or load encryption key"""
        # Get encryption key from environment
        encryption_key = os.getenv('ENCRYPTION_KEY')
        
        if not encryption_key:
            logger.warning("⚠️ ENCRYPTION_KEY not set. Using default (NOT SECURE FOR PRODUCTION)")
            # Generate a key from app secret (NOT RECOMMENDED FOR PRODUCTION)
            secret = os.getenv('JWT_SECRET_KEY', 'default-secret-key').encode()
            salt = b'smart-hiring-salt'  # Should be stored securely
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(secret))
            self._fernet = Fernet(key)
        else:
            # Use provided encryption key
            try:
                self._fernet = Fernet(encryption_key.encode())
            except Exception as e:
                logger.error(f"❌ Invalid ENCRYPTION_KEY: {e}")
                raise
    
    def encrypt(self, plaintext: str) -> Optional[str]:
        """
        Encrypt a string
        
        Args:
            plaintext: String to encrypt
        
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return None
        
        try:
            encrypted_bytes = self._fernet.encrypt(plaintext.encode())
            return base64.urlsafe_b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"❌ Encryption failed: {e}")
            return None
    
    def decrypt(self, ciphertext: str) -> Optional[str]:
        """
        Decrypt a string
        
        Args:
            ciphertext: Base64-encoded encrypted string
        
        Returns:
            Decrypted plaintext
        """
        if not ciphertext:
            return None
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"❌ Decryption failed: {e}")
            return None
    
    def encrypt_dict_fields(self, data: dict, fields: list) -> dict:
        """
        Encrypt specific fields in a dictionary
        
        Args:
            data: Dictionary containing data
            fields: List of field names to encrypt
        
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_value = self.encrypt(str(encrypted_data[field]))
                if encrypted_value:
                    encrypted_data[field] = encrypted_value
                    encrypted_data[f"{field}_encrypted"] = True
        
        return encrypted_data
    
    def decrypt_dict_fields(self, data: dict, fields: list) -> dict:
        """
        Decrypt specific fields in a dictionary
        
        Args:
            data: Dictionary containing encrypted data
            fields: List of field names to decrypt
        
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        
        for field in fields:
            if field in decrypted_data and decrypted_data.get(f"{field}_encrypted"):
                decrypted_value = self.decrypt(decrypted_data[field])
                if decrypted_value:
                    decrypted_data[field] = decrypted_value
                    del decrypted_data[f"{field}_encrypted"]
        
        return decrypted_data
    
    @staticmethod
    def hash_sensitive_field(value: str) -> str:
        """
        One-way hash for sensitive fields (e.g., SSN for search)
        
        Args:
            value: Value to hash
        
        Returns:
            Hex-encoded hash
        """
        import hashlib
        return hashlib.sha256(value.encode()).hexdigest()
    
    @staticmethod
    def mask_pii(value: str, visible_chars: int = 4, mask_char: str = '*') -> str:
        """
        Mask PII for display (e.g., phone number, SSN)
        
        Args:
            value: Value to mask
            visible_chars: Number of characters to keep visible
            mask_char: Character to use for masking
        
        Returns:
            Masked string
        
        Example:
            mask_pii('1234567890', 4) -> '******7890'
            mask_pii('john@example.com', 3) -> '*************com'
        """
        if not value or len(value) <= visible_chars:
            return value
        
        masked_length = len(value) - visible_chars
        return mask_char * masked_length + value[-visible_chars:]


# Global encryption manager instance
encryption_manager = EncryptionManager()


# Fields that should be encrypted in database
PII_FIELDS = [
    'ssn',
    'social_security_number',
    'national_id',
    'passport_number',
    'phone_number',
    'date_of_birth',
    'address',
    'salary_expectation',
    'compensation'
]


def encrypt_pii_fields(data: dict) -> dict:
    """
    Encrypt PII fields in data dictionary
    
    Args:
        data: Dictionary containing potential PII
    
    Returns:
        Dictionary with PII fields encrypted
    """
    return encryption_manager.encrypt_dict_fields(data, PII_FIELDS)


def decrypt_pii_fields(data: dict) -> dict:
    """
    Decrypt PII fields in data dictionary
    
    Args:
        data: Dictionary containing encrypted PII
    
    Returns:
        Dictionary with PII fields decrypted
    """
    return encryption_manager.decrypt_dict_fields(data, PII_FIELDS)
