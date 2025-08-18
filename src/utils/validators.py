"""
Validation utilities for files and data with comprehensive error checking. 

This module provides robust validation for steganography operations
including file format checking, security validation, and data integrity.
"""

import os
import logging
from typing import List, Optional, Tuple, Dict, Any
from PIL import Image
import numpy as np


class FileValidator:
    """
    Validates files and data for steganography operations with enhanced security.

    Provides comprehensive validation including format checking, size limits,
    security scanning, and data integrity verification.
    """

    SUPPORTED_EXTENSIONS = {'.png', '.bmp', '.tiff', '.tif'}
    MAX_FILE_SIZE_MB = 50  # Maximum file size in MB
    MIN_IMAGE_DIMENSION = 10  # Minimum width/height in pixels
    MAX_IMAGE_DIMENSION = 10000  # Maximum width/height in pixels

    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """Get list of supported image formats."""
        return list(cls.SUPPORTED_EXTENSIONS)
    
    @classmethod
    def validate_image_file(cls, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate image file for steganography.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Check file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > cls.MAX_FILE_SIZE_MB:
            return False, f"File too large. Maximum size: {cls.MAX_FILE_SIZE_MB}MB"
        
        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        if ext not in cls.SUPPORTED_EXTENSIONS:
            return False, f"Unsupported format. Supported: {', '.join(cls.SUPPORTED_EXTENSIONS)}"
        
        # Try to open image
        try:
            with Image.open(file_path) as img:
                # Check image mode
                if img.mode not in ['RGB', 'RGBA', 'L']:
                    return False, f"Unsupported image mode: {img.mode}"
                
                # Check minimum dimensions
                if img.width < cls.MIN_IMAGE_DIMENSION or img.height < cls.MIN_IMAGE_DIMENSION:
                    return False, f"Image too small (minimum {cls.MIN_IMAGE_DIMENSION}x{cls.MIN_IMAGE_DIMENSION} pixels)"

                # Check maximum dimensions
                if img.width > cls.MAX_IMAGE_DIMENSION or img.height > cls.MAX_IMAGE_DIMENSION:
                    return False, f"Image too large (maximum {cls.MAX_IMAGE_DIMENSION}x{cls.MAX_IMAGE_DIMENSION} pixels)"
                
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
        
        return True, None
    
    @classmethod
    def validate_message(cls, message: str, max_length: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate message for steganography.
        
        Args:
            message: Message to validate
            max_length: Maximum allowed length
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not message or not message.strip():
            return False, "Message cannot be empty"
        
        if max_length and len(message) > max_length:
            return False, f"Message too long. Maximum: {max_length} characters"
        
        # Check for valid UTF-8 encoding
        try:
            message.encode('utf-8')
        except UnicodeEncodeError:
            return False, "Message contains invalid characters"
        
        # Check for null bytes (can cause issues)
        if '\x00' in message:
            return False, "Message cannot contain null bytes"
        
        return True, None
    
    @classmethod
    def estimate_capacity(cls, image_path: str) -> Optional[int]:
        """
        Estimate steganographic capacity of an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Estimated capacity in characters, or None if error
        """
        # Input validation
        if not image_path or not image_path.strip():
            return None
        
        if not os.path.exists(image_path):
            return None
        
        try:
            with Image.open(image_path) as img:
                # Check minimum dimensions
                if img.width < cls.MIN_IMAGE_DIMENSION or img.height < cls.MIN_IMAGE_DIMENSION:
                    return None
                
                # LSB capacity: roughly 1 bit per pixel channel
                total_pixels = img.width * img.height
                if img.mode == 'RGB':
                    capacity_bits = total_pixels * 3  # 3 channels
                elif img.mode == 'RGBA':
                    capacity_bits = total_pixels * 4  # 4 channels
                else:  # Grayscale
                    capacity_bits = total_pixels
                
                # Convert to characters (8 bits per char) and reserve space for delimiter
                capacity_chars = (capacity_bits // 8) - 20  # Reserve 20 chars for delimiter
                return max(0, capacity_chars)
                
        except Exception:
            return None

    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Validate password strength with detailed analysis.

        Args:
            password: Password to validate

        Returns:
            Tuple of (is_valid, error_message, strength_info)
        """
        if not password:
            return False, "Password cannot be empty", {}

        # Check minimum length
        if len(password) < 8:
            return False, "Password must be at least 8 characters long", {}

        # Analyze password strength
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

        strength_score = sum([has_upper, has_lower, has_digit, has_special])

        strength_info = {
            'length': len(password),
            'has_uppercase': has_upper,
            'has_lowercase': has_lower,
            'has_digits': has_digit,
            'has_special': has_special,
            'strength_score': strength_score,
            'strength_level': cls._get_strength_level(strength_score, len(password))
        }

        # Require at least 3 out of 4 character types
        if strength_score < 3:
            return False, "Password must contain at least 3 of: uppercase, lowercase, digits, special characters", strength_info

        return True, None, strength_info

    @classmethod
    def _get_strength_level(cls, score: int, length: int) -> str:
        """Get password strength level description."""
        if score >= 4 and length >= 12:
            return "Very Strong"
        elif score >= 3 and length >= 10:
            return "Strong"
        elif score >= 3 and length >= 8:
            return "Medium"
        else:
            return "Weak"

    @classmethod
    def validate_image_integrity(cls, image_array: np.ndarray) -> Tuple[bool, Optional[str]]:
        """
        Validate image data integrity.

        Args:
            image_array: Image as numpy array

        Returns:
            Tuple of (is_valid, error_message)
        """
        if image_array is None:
            return False, "Image array is None"

        if image_array.size == 0:
            return False, "Image array is empty"

        # Check data type
        if image_array.dtype not in [np.uint8, np.uint16]:
            return False, f"Unsupported image data type: {image_array.dtype}"

        # Check dimensions
        if len(image_array.shape) not in [2, 3]:
            return False, f"Invalid image dimensions: {image_array.shape}"

        if len(image_array.shape) == 3 and image_array.shape[2] not in [1, 3, 4]:
            return False, f"Invalid number of channels: {image_array.shape[2]}"

        # Check value ranges
        if image_array.dtype == np.uint8:
            if np.any(image_array < 0) or np.any(image_array > 255):
                return False, "Image values out of range for uint8 (0-255)"

        return True, None

    @classmethod
    def scan_for_existing_steganography(cls, image_array: np.ndarray) -> Dict[str, Any]:
        """
        Basic scan for potential existing steganographic content.

        Args:
            image_array: Image to scan

        Returns:
            Dictionary with scan results
        """
        results = {
            'suspicious_patterns': False,
            'lsb_randomness': 0.0,
            'recommendations': []
        }

        try:
            # Analyze LSB randomness (basic check)
            if len(image_array.shape) >= 2:
                flat_image = image_array.flatten()
                lsb_bits = flat_image & 1  # Extract LSBs

                # Calculate randomness (simple entropy measure)
                unique_vals, counts = np.unique(lsb_bits, return_counts=True)
                if len(unique_vals) > 1:
                    probabilities = counts / len(lsb_bits)
                    entropy = -np.sum(probabilities * np.log2(probabilities))
                    results['lsb_randomness'] = entropy

                    # High randomness might indicate existing steganography
                    if entropy > 0.9:
                        results['suspicious_patterns'] = True
                        results['recommendations'].append("High LSB randomness detected - may contain hidden data")

        except Exception as e:
            logging.warning(f"Error during steganography scan: {e}")
            results['recommendations'].append("Could not complete steganography scan")

        return results
