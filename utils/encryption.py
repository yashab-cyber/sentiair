"""
Data encryption utilities for Sentinair
Handles encryption/decryption of sensitive data
"""

import os
import logging
from typing import Union, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class DataEncryption:
    """Data encryption manager for Sentinair"""
    
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.fernet = None
        
        # Initialize encryption if enabled
        if config.get('security.encrypt_logs', True):
            self._initialize_encryption()
            
    def _initialize_encryption(self):
        """Initialize encryption with key from file"""
        try:
            key_path = self.config.get_encryption_key_path()
            
            if os.path.exists(key_path):
                with open(key_path, 'rb') as key_file:
                    key = key_file.read()
                self.fernet = Fernet(key)
                self.logger.info("Encryption initialized successfully")
            else:
                self.logger.warning(f"Encryption key not found at {key_path}")
                self._generate_and_save_key()
                
        except Exception as e:
            self.logger.error(f"Error initializing encryption: {e}")
            
    def _generate_and_save_key(self):
        """Generate new encryption key and save it"""
        try:
            key = Fernet.generate_key()
            key_path = self.config.get_encryption_key_path()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(key_path), exist_ok=True)
            
            with open(key_path, 'wb') as key_file:
                key_file.write(key)
                
            # Set restrictive permissions
            os.chmod(key_path, 0o600)
            
            self.fernet = Fernet(key)
            self.logger.info("New encryption key generated and saved")
            
        except Exception as e:
            self.logger.error(f"Error generating encryption key: {e}")
            
    def encrypt(self, data: Union[str, bytes]) -> Optional[str]:
        """Encrypt data and return base64 encoded string"""
        try:
            if not self.fernet:
                return None
                
            if isinstance(data, str):
                data = data.encode('utf-8')
                
            encrypted_data = self.fernet.encrypt(data)
            return base64.b64encode(encrypted_data).decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Error encrypting data: {e}")
            return None
            
    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """Decrypt base64 encoded encrypted data"""
        try:
            if not self.fernet:
                return None
                
            encrypted_bytes = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted_data = self.fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode('utf-8')
            
        except Exception as e:
            self.logger.error(f"Error decrypting data: {e}")
            return None
            
    def encrypt_file(self, file_path: str, output_path: str = None) -> bool:
        """Encrypt a file"""
        try:
            if not self.fernet:
                return False
                
            if output_path is None:
                output_path = file_path + '.encrypted'
                
            with open(file_path, 'rb') as input_file:
                file_data = input_file.read()
                
            encrypted_data = self.fernet.encrypt(file_data)
            
            with open(output_path, 'wb') as output_file:
                output_file.write(encrypted_data)
                
            self.logger.info(f"File encrypted: {file_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error encrypting file {file_path}: {e}")
            return False
            
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> bool:
        """Decrypt a file"""
        try:
            if not self.fernet:
                return False
                
            if output_path is None:
                output_path = encrypted_file_path.replace('.encrypted', '')
                
            with open(encrypted_file_path, 'rb') as encrypted_file:
                encrypted_data = encrypted_file.read()
                
            decrypted_data = self.fernet.decrypt(encrypted_data)
            
            with open(output_path, 'wb') as output_file:
                output_file.write(decrypted_data)
                
            self.logger.info(f"File decrypted: {encrypted_file_path} -> {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error decrypting file {encrypted_file_path}: {e}")
            return False
            
    def is_encryption_enabled(self) -> bool:
        """Check if encryption is enabled and available"""
        return self.fernet is not None
        
    def secure_delete(self, file_path: str) -> bool:
        """Securely delete a file by overwriting it"""
        try:
            if not os.path.exists(file_path):
                return True
                
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Overwrite with random data multiple times
            with open(file_path, 'r+b') as file:
                for _ in range(3):  # Overwrite 3 times
                    file.seek(0)
                    file.write(os.urandom(file_size))
                    file.flush()
                    os.fsync(file.fileno())
                    
            # Finally delete the file
            os.remove(file_path)
            
            self.logger.info(f"File securely deleted: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error securely deleting file {file_path}: {e}")
            return False
            
    def generate_password_hash(self, password: str, salt: bytes = None) -> tuple:
        """Generate a secure password hash with salt"""
        try:
            if salt is None:
                salt = os.urandom(32)
                
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            key = kdf.derive(password.encode('utf-8'))
            hash_value = base64.b64encode(key).decode('utf-8')
            salt_value = base64.b64encode(salt).decode('utf-8')
            
            return hash_value, salt_value
            
        except Exception as e:
            self.logger.error(f"Error generating password hash: {e}")
            return None, None
            
    def verify_password_hash(self, password: str, hash_value: str, salt_value: str) -> bool:
        """Verify a password against its hash"""
        try:
            salt = base64.b64decode(salt_value.encode('utf-8'))
            stored_hash = base64.b64decode(hash_value.encode('utf-8'))
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            
            kdf.verify(password.encode('utf-8'), stored_hash)
            return True
            
        except Exception as e:
            self.logger.debug(f"Password verification failed: {e}")
            return False
