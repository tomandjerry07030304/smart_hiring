"""
File Security Module
Handles virus scanning, secure storage, signed URLs
"""

import os
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class FileSecurityManager:
    """Manages secure file operations"""
    
    # Allowed file extensions
    ALLOWED_RESUME_EXTENSIONS = {'.pdf', '.doc', '.docx', '.txt', '.rtf'}
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
    
    # Maximum file sizes (bytes)
    MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_IMAGE_SIZE = 5 * 1024 * 1024    # 5 MB
    
    def __init__(self):
        """Initialize file security manager"""
        self.upload_folder = os.getenv('UPLOAD_FOLDER', 'backend/uploads')
        self.enable_virus_scan = os.getenv('ENABLE_VIRUS_SCAN', 'false').lower() == 'true'
    
    def is_allowed_file(self, filename: str, file_type: str = 'resume') -> bool:
        """
        Check if file extension is allowed
        
        Args:
            filename: Name of the file
            file_type: Type of file ('resume', 'image')
        
        Returns:
            True if allowed
        """
        if '.' not in filename:
            return False
        
        ext = os.path.splitext(filename)[1].lower()
        
        if file_type == 'resume':
            return ext in self.ALLOWED_RESUME_EXTENSIONS
        elif file_type == 'image':
            return ext in self.ALLOWED_IMAGE_EXTENSIONS
        
        return False
    
    def validate_file_size(self, file_size: int, file_type: str = 'resume') -> Tuple[bool, Optional[str]]:
        """
        Validate file size
        
        Args:
            file_size: Size of file in bytes
            file_type: Type of file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        max_size = self.MAX_RESUME_SIZE if file_type == 'resume' else self.MAX_IMAGE_SIZE
        
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            return False, f"File too large. Maximum size: {max_mb:.1f} MB"
        
        if file_size == 0:
            return False, "File is empty"
        
        return True, None
    
    def generate_secure_filename(self, original_filename: str, user_id: str) -> str:
        """
        Generate secure filename
        
        Args:
            original_filename: Original filename
            user_id: User ID
        
        Returns:
            Secure filename
        """
        # Get file extension
        ext = os.path.splitext(original_filename)[1].lower()
        
        # Generate hash from user_id + timestamp + original filename
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{user_id}_{timestamp}_{original_filename}"
        file_hash = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        # Create secure filename
        return f"{user_id}_{file_hash}{ext}"
    
    def scan_file_for_viruses(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Scan file for viruses using ClamAV
        
        Args:
            file_path: Path to file
        
        Returns:
            Tuple of (is_safe, threat_name)
        """
        if not self.enable_virus_scan:
            logger.info("Virus scanning disabled")
            return True, None
        
        try:
            import pyclamd
            
            # Connect to ClamAV daemon
            cd = pyclamd.ClamdUnixSocket()
            
            # Check if ClamAV is available
            if not cd.ping():
                logger.warning("⚠️ ClamAV not available, skipping virus scan")
                return True, None
            
            # Scan file
            scan_result = cd.scan_file(file_path)
            
            if scan_result is None:
                # No threat found
                logger.info(f"✅ File scan clean: {file_path}")
                return True, None
            else:
                # Threat found
                threat_name = scan_result[file_path][1]
                logger.warning(f"🚨 Virus detected: {threat_name} in {file_path}")
                return False, threat_name
                
        except ImportError:
            logger.warning("⚠️ pyclamd not installed, skipping virus scan")
            return True, None
        except Exception as e:
            logger.error(f"❌ Virus scan error: {e}")
            # Fail-safe: allow file if scan fails (or set to False for strict mode)
            return True, None
    
    def sanitize_file_content(self, file_path: str, file_type: str) -> bool:
        """
        Sanitize file content (basic checks)
        
        Args:
            file_path: Path to file
            file_type: Type of file
        
        Returns:
            True if safe
        """
        try:
            # Check MIME type matches extension
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if file_type == 'resume':
                allowed_mimes = {
                    'application/pdf',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'text/plain',
                    'text/rtf'
                }
                
                if mime_type not in allowed_mimes:
                    logger.warning(f"⚠️ Suspicious MIME type: {mime_type}")
                    return False
            
            # Basic content validation
            with open(file_path, 'rb') as f:
                # Check file signature (magic bytes)
                header = f.read(512)
                
                # PDF check
                if file_path.endswith('.pdf'):
                    if not header.startswith(b'%PDF'):
                        logger.warning("⚠️ Invalid PDF signature")
                        return False
                
                # Check for suspicious content
                suspicious_patterns = [
                    b'<script',
                    b'javascript:',
                    b'<?php',
                    b'<%',
                    b'eval(',
                ]
                
                for pattern in suspicious_patterns:
                    if pattern in header:
                        logger.warning(f"⚠️ Suspicious content detected: {pattern}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ File sanitization error: {e}")
            return False
    
    def create_secure_storage_path(self, user_id: str, file_type: str) -> str:
        """
        Create secure storage path for file
        
        Args:
            user_id: User ID
            file_type: Type of file
        
        Returns:
            Storage path
        """
        # Organize files by type and user ID
        base_path = os.path.join(self.upload_folder, file_type, user_id[:2], user_id)
        os.makedirs(base_path, exist_ok=True)
        return base_path
    
    def generate_signed_url(
        self,
        file_path: str,
        expiry_hours: int = 24
    ) -> Tuple[str, datetime]:
        """
        Generate signed URL for secure file access
        
        Args:
            file_path: Path to file
            expiry_hours: Hours until URL expires
        
        Returns:
            Tuple of (signed_url, expiry_time)
        """
        # Generate signature
        expiry_time = datetime.utcnow() + timedelta(hours=expiry_hours)
        expiry_timestamp = int(expiry_time.timestamp())
        
        # Create signature from file_path + expiry + secret
        secret = os.getenv('JWT_SECRET_KEY', 'default-secret')
        signature_input = f"{file_path}_{expiry_timestamp}_{secret}"
        signature = hashlib.sha256(signature_input.encode()).hexdigest()
        
        # Create signed URL
        signed_url = f"/api/files/download?path={file_path}&expires={expiry_timestamp}&signature={signature}"
        
        return signed_url, expiry_time
    
    def verify_signed_url(self, file_path: str, expiry_timestamp: int, signature: str) -> bool:
        """
        Verify signed URL
        
        Args:
            file_path: Path to file
            expiry_timestamp: Expiry timestamp
            signature: URL signature
        
        Returns:
            True if valid
        """
        try:
            # Check expiry
            if datetime.utcnow().timestamp() > expiry_timestamp:
                logger.warning("⚠️ Signed URL expired")
                return False
            
            # Verify signature
            secret = os.getenv('JWT_SECRET_KEY', 'default-secret')
            signature_input = f"{file_path}_{expiry_timestamp}_{secret}"
            expected_signature = hashlib.sha256(signature_input.encode()).hexdigest()
            
            if signature != expected_signature:
                logger.warning("⚠️ Invalid signature")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Signature verification error: {e}")
            return False
    
    def delete_file_securely(self, file_path: str):
        """
        Securely delete file (overwrite before deletion)
        
        Args:
            file_path: Path to file
        """
        try:
            if os.path.exists(file_path):
                # Get file size
                file_size = os.path.getsize(file_path)
                
                # Overwrite with random data (simple secure deletion)
                with open(file_path, 'wb') as f:
                    f.write(os.urandom(file_size))
                
                # Delete file
                os.remove(file_path)
                logger.info(f"🗑️ File securely deleted: {file_path}")
        except Exception as e:
            logger.error(f"❌ Secure deletion failed: {e}")


# Global file security manager instance
file_security_manager = FileSecurityManager()
