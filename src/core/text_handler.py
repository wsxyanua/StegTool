""" Text processing utilities for steganography with secure encryption. """

import base64
import secrets
import logging
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


class TextHandler:
    """Handles text encoding, encryption, and validation with AES-256 security."""

    # Security constants
    SALT_SIZE = 32  # 256 bits
    IV_SIZE = 16    # 128 bits for AES
    KEY_SIZE = 32   # 256 bits for AES-256
    PBKDF2_ITERATIONS = 100000  # OWASP recommended minimum

    @staticmethod
    def _validate_password(password: str) -> None:
        """Validate password strength."""
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        strength_score = sum([has_upper, has_lower, has_digit, has_special])
        if strength_score < 3:
            logging.warning("Weak password detected. Consider using uppercase, lowercase, digits, and special characters.")

    @staticmethod
    def _derive_key(password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=TextHandler.KEY_SIZE,
            salt=salt,
            iterations=TextHandler.PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))

    @staticmethod
    def _encrypt_aes(plaintext: str, password: str) -> str:
        """Encrypt plaintext using AES-256-CBC with PBKDF2 key derivation."""
        # Generate random salt and IV
        salt = secrets.token_bytes(TextHandler.SALT_SIZE)
        iv = secrets.token_bytes(TextHandler.IV_SIZE)

        # Derive key from password
        key = TextHandler._derive_key(password, salt)

        # Pad plaintext to AES block size (16 bytes)
        plaintext_bytes = plaintext.encode('utf-8')
        padding_length = 16 - (len(plaintext_bytes) % 16)
        padded_plaintext = plaintext_bytes + bytes([padding_length] * padding_length)

        # Encrypt
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

        # Combine salt + iv + ciphertext and encode as base64
        encrypted_data = salt + iv + ciphertext
        return base64.b64encode(encrypted_data).decode('ascii')

    @staticmethod
    def _decrypt_aes(encrypted_data: str, password: str) -> str:
        """Decrypt AES-256-CBC encrypted data."""
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))

            # Extract salt, IV, and ciphertext
            salt = encrypted_bytes[:TextHandler.SALT_SIZE]
            iv = encrypted_bytes[TextHandler.SALT_SIZE:TextHandler.SALT_SIZE + TextHandler.IV_SIZE]
            ciphertext = encrypted_bytes[TextHandler.SALT_SIZE + TextHandler.IV_SIZE:]

            # Derive key from password
            key = TextHandler._derive_key(password, salt)

            # Decrypt
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            # Remove padding with validation
            if len(padded_plaintext) == 0:
                raise ValueError("Invalid decryption result")

            padding_length = padded_plaintext[-1]

            # Validate padding
            if padding_length > 16 or padding_length == 0:
                raise ValueError("Invalid padding - wrong password or corrupted data")

            if len(padded_plaintext) < padding_length:
                raise ValueError("Invalid padding length")

            # Check if padding is valid
            for i in range(padding_length):
                if padded_plaintext[-(i+1)] != padding_length:
                    raise ValueError("Invalid padding - wrong password")

            plaintext = padded_plaintext[:-padding_length]

            return plaintext.decode('utf-8')

        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}. Check password or data integrity.")

    @staticmethod
    def prepare_message(message: str, password: Optional[str] = None,
                       encode_base64: bool = False) -> str:
        """
        Prepare message for encoding with AES encryption and optional base64 encoding.

        Args:
            message: Original message to prepare
            password: Optional password for AES-256 encryption
            encode_base64: Whether to base64 encode the final result

        Returns:
            Processed message ready for steganography

        Raises:
            ValueError: If message is empty or password validation fails
        """
        # Input validation
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        processed = message

        # AES encryption if password provided
        if password:
            if not password.strip():
                raise ValueError("Password cannot be empty if provided")

            # Validate password strength
            TextHandler._validate_password(password)

            # Encrypt with AES-256
            processed = TextHandler._encrypt_aes(processed, password)
            logging.info("Message encrypted with AES-256-CBC")

        # Base64 encoding if requested (additional layer)
        if encode_base64:
            processed = base64.b64encode(processed.encode()).decode()
            logging.info("Message encoded with base64")

        return processed
    
    @staticmethod
    def process_decoded_message(message: str, password: Optional[str] = None,
                              decode_base64: bool = False) -> str:
        """
        Process decoded message with AES decryption and optional base64 decoding.

        Args:
            message: Decoded message from steganography
            password: Optional password for AES-256 decryption
            decode_base64: Whether to base64 decode before decryption

        Returns:
            Final processed message

        Raises:
            ValueError: If decryption fails or message is invalid
        """
        # Input validation
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        processed = message

        try:
            # Base64 decoding if requested (reverse order from encoding)
            if decode_base64:
                processed = base64.b64decode(processed.encode()).decode()
                logging.info("Message decoded from base64")

            # AES decryption if password provided
            if password:
                if not password.strip():
                    raise ValueError("Password cannot be empty if provided")

                processed = TextHandler._decrypt_aes(processed, password)
                logging.info("Message decrypted with AES-256-CBC")

        except Exception as e:
            raise ValueError(f"Error processing decoded message: {str(e)}")

        return processed

    @staticmethod
    def validate_message(message: str, max_length: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate message for steganography with detailed error reporting.

        Args:
            message: Message to validate
            max_length: Optional maximum length limit

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not message or not message.strip():
            return False, "Message cannot be empty"

        # Check for valid UTF-8 encoding
        try:
            message.encode('utf-8')
        except UnicodeEncodeError:
            return False, "Message contains invalid UTF-8 characters"

        # Check for null bytes (can cause issues in steganography)
        if '\x00' in message:
            return False, "Message cannot contain null bytes"

        # Check length limit
        if max_length and len(message) > max_length:
            return False, f"Message too long. Maximum: {max_length} characters"

        # Check for potentially problematic characters
        control_chars = [c for c in message if ord(c) < 32 and c not in '\t\n\r']
        if control_chars:
            logging.warning(f"Message contains {len(control_chars)} control characters")

        return True, None

    @staticmethod
    def get_message_stats(message: str) -> dict:
        """Get detailed statistics about the message."""
        return {
            'length': len(message),
            'bytes': len(message.encode('utf-8')),
            'lines': message.count('\n') + 1,
            'words': len(message.split()),
            'chars_alphanumeric': sum(c.isalnum() for c in message),
            'chars_whitespace': sum(c.isspace() for c in message),
            'chars_special': sum(not c.isalnum() and not c.isspace() for c in message),
            'entropy': TextHandler._calculate_entropy(message)
        }

    @staticmethod
    def _calculate_entropy(text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0

        # Count character frequencies
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1

        # Calculate entropy using proper Shannon entropy formula
        import math
        entropy = 0.0
        text_length = len(text)
        for count in char_counts.values():
            probability = count / text_length
            if probability > 0:
                entropy -= probability * math.log2(probability)

        return entropy
