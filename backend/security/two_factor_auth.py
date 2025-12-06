"""
Two-Factor Authentication (2FA) Implementation
Supports TOTP (Time-based One-Time Password)
"""

import io
import base64
from typing import Tuple, Optional
import logging

# Optional dependencies - graceful degradation if not available
try:
    import pyotp
    PYOTP_AVAILABLE = True
except ImportError:
    PYOTP_AVAILABLE = False
    pyotp = None
    logging.warning("pyotp not available - 2FA disabled")

try:
    import qrcode
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False
    qrcode = None
    logging.warning("qrcode not available - QR code generation disabled")

logger = logging.getLogger(__name__)


class TwoFactorAuth:
    """Manages two-factor authentication"""
    
    @staticmethod
    def generate_secret() -> str:
        """
        Generate a new TOTP secret
        
        Returns:
            Base32-encoded secret
        """
        if not PYOTP_AVAILABLE:
            raise RuntimeError("pyotp not available - cannot generate secret")
        return pyotp.random_base32()
    
    @staticmethod
    def get_provisioning_uri(secret: str, email: str, issuer_name: str = "Smart Hiring") -> str:
        """
        Get provisioning URI for QR code
        
        Args:
            secret: TOTP secret
            email: User's email
            issuer_name: Name of the service
        
        Returns:
            Provisioning URI
        """
        if not PYOTP_AVAILABLE:
            raise RuntimeError("pyotp not available - cannot generate provisioning URI")
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=email,
            issuer_name=issuer_name
        )
    
    @staticmethod
    def generate_qr_code(provisioning_uri: str) -> str:
        """
        Generate QR code for 2FA setup
        
        Args:
            provisioning_uri: TOTP provisioning URI
        
        Returns:
            Base64-encoded QR code image
        """
        if not QRCODE_AVAILABLE:
            logger.warning("qrcode not available - cannot generate QR code")
            return ""
            
        try:
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Failed to generate QR code: {e}")
            return ""
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """
        Verify a TOTP token
        
        Args:
            secret: User's TOTP secret
            token: 6-digit token to verify
        
        Returns:
            True if valid, False otherwise
        """
        if not PYOTP_AVAILABLE:
            logger.warning("pyotp not available - 2FA verification disabled")
            return False
            
        try:
            totp = pyotp.TOTP(secret)
            # Verify with 1-step tolerance for clock skew
            return totp.verify(token, valid_window=1)
        except Exception as e:
            logger.error(f"Failed to verify token: {e}")
            return False
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> list:
        """
        Generate backup codes for 2FA recovery
        
        Args:
            count: Number of backup codes to generate
        
        Returns:
            List of backup codes
        """
        import secrets
        codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice('ABCDEFGHJKLMNPQRSTUVWXYZ23456789') for _ in range(8))
            # Format as XXXX-XXXX
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes
    
    @staticmethod
    def hash_backup_code(code: str) -> str:
        """
        Hash a backup code for storage
        
        Args:
            code: Backup code to hash
        
        Returns:
            Hashed code
        """
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()
    
    @staticmethod
    def verify_backup_code(code: str, hashed_codes: list) -> Tuple[bool, Optional[str]]:
        """
        Verify a backup code
        
        Args:
            code: Backup code to verify
            hashed_codes: List of hashed backup codes
        
        Returns:
            Tuple of (is_valid, matched_hash)
        """
        hashed = TwoFactorAuth.hash_backup_code(code)
        if hashed in hashed_codes:
            return True, hashed
        return False, None
