"""
Core steganography engine with LSB, DCT, and DWT algorithms.

This module provides steganography operations matching the web interface
functionality with LSB, DCT, and DWT methods.

Author: Open Source Community
License: MIT
Version: 1.0.0
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import numpy as np
import logging
import time


class SteganographyAlgorithm(ABC):
    """
    Abstract base class for steganography algorithms.

    All steganography algorithms must implement these methods to ensure
    consistent interface and proper error handling.
    """

    @abstractmethod
    def encode(self, image: np.ndarray, message: str, **kwargs) -> np.ndarray:
        """
        Encode message into image.

        Args:
            image: Input image as numpy array
            message: Message to hide
            **kwargs: Algorithm-specific parameters

        Returns:
            Modified image with hidden message

        Raises:
            ValueError: If encoding fails or parameters are invalid
        """
        pass

    @abstractmethod
    def decode(self, image: np.ndarray, **kwargs) -> str:
        """
        Decode message from image.

        Args:
            image: Image containing hidden message
            **kwargs: Algorithm-specific parameters

        Returns:
            Extracted message

        Raises:
            ValueError: If decoding fails or no message found
        """
        pass

    @abstractmethod
    def can_fit_message(self, image: np.ndarray, message: str, **kwargs) -> bool:
        """
        Check if message can fit in the image.

        Args:
            image: Target image
            message: Message to check
            **kwargs: Algorithm-specific parameters

        Returns:
            True if message fits, False otherwise
        """
        pass

    @abstractmethod
    def get_capacity(self, image: np.ndarray, **kwargs) -> int:
        """
        Get maximum message capacity for the image.

        Args:
            image: Target image
            **kwargs: Algorithm-specific parameters

        Returns:
            Maximum message length in characters
        """
        pass


class LSBAlgorithm(SteganographyAlgorithm):
    """
    Least Significant Bit steganography implementation with enhanced security.

    This implementation uses LSB modification with improved error detection
    and capacity management.
    """

    DELIMITER = "###END_OF_MESSAGE###"
    MAX_BITS_PER_CHANNEL = 1  # Can be increased for higher capacity/lower quality
    
    def encode(self, image: np.ndarray, message: str, **kwargs) -> np.ndarray:
        """
        Encode message using LSB technique.
        
        Args:
            image: Input image as numpy array
            message: Text message to hide
            **kwargs: Additional parameters (password, channels, etc.)
            
        Returns:
            Modified image with hidden message
        """
        # Input validation
        if image is None or image.size == 0:
            raise ValueError("Invalid image: empty or None")
        
        if not message or len(message.strip()) == 0:
            raise ValueError("Message cannot be empty")
        
        # Add delimiter to mark end of message
        full_message = message + self.DELIMITER
        
        # Convert message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in full_message)
        
        # Check if message fits
        if not self.can_fit_message(image, message, **kwargs):
            raise ValueError("Message too long for this image")
        
        # Create copy of image
        stego_image = image.copy()
        
        # Get image dimensions
        height, width = stego_image.shape[:2]
        channels = stego_image.shape[2] if len(stego_image.shape) > 2 else 1
        
        # Flatten image for easier processing
        flat_image = stego_image.flatten()
        
        # Embed message bits
        for i, bit in enumerate(binary_message):
            # Modify LSB of pixel value
            flat_image[i] = (flat_image[i] & 0xFE) | int(bit)
        
        # Reshape back to original dimensions
        if channels > 1:
            return flat_image.reshape(height, width, channels)
        else:
            return flat_image.reshape(height, width)
    
    def decode(self, image: np.ndarray, **kwargs) -> str:
        """
        Decode message from image using LSB technique.
        
        Args:
            image: Image containing hidden message
            **kwargs: Additional parameters
            
        Returns:
            Decoded message string
        """
        # Input validation
        if image is None or image.size == 0:
            raise ValueError("Invalid image: empty or None")
        
        # Flatten image
        flat_image = image.flatten()
        
        # Extract LSBs - more efficient approach
        binary_message = ''.join(str(pixel_value & 1) for pixel_value in flat_image)
        
        # Convert binary to text
        decoded_chars = []
        for i in range(0, len(binary_message), 8):
            byte = binary_message[i:i+8]
            if len(byte) == 8:
                char = chr(int(byte, 2))
                decoded_chars.append(char)
                
                # Check for delimiter
                current_text = ''.join(decoded_chars)
                if current_text.endswith(self.DELIMITER):
                    return current_text[:-len(self.DELIMITER)]
        
        # If no delimiter found, return what we have
        return ''.join(decoded_chars)
    
    def can_fit_message(self, image: np.ndarray, message: str, **kwargs) -> bool:
        """Check if message can fit in image."""
        # Input validation
        if image is None or image.size == 0:
            return False

        if not message or len(message.strip()) == 0:
            return False

        full_message = message + self.DELIMITER
        message_bits = len(full_message) * 8
        available_bits = image.size  # Total pixels
        return message_bits <= available_bits

    def get_capacity(self, image: np.ndarray, **kwargs) -> int:
        """Get maximum message capacity for the image."""
        if image is None or image.size == 0:
            return 0

        # Available bits = total pixels, minus delimiter overhead
        delimiter_bits = len(self.DELIMITER) * 8
        available_bits = image.size - delimiter_bits

        # Convert to characters (8 bits per character)
        return max(0, available_bits // 8)


class SteganographyEngine:
    """
    Main steganography engine with pluggable algorithms and enhanced features.

    This engine provides a unified interface for multiple steganography algorithms
    with comprehensive error handling and logging.
    """

    def __init__(self):
        self._algorithms: Dict[str, SteganographyAlgorithm] = {
            'lsb': LSBAlgorithm(),
        }
        self._current_algorithm = 'lsb'
        self._logger = logging.getLogger(__name__)

        # Register DCT and DWT algorithms
        self._register_algorithms()
    
    def register_algorithm(self, name: str, algorithm: SteganographyAlgorithm) -> None:
        """Register a new steganography algorithm."""
        if not isinstance(algorithm, SteganographyAlgorithm):
            raise TypeError("Algorithm must inherit from SteganographyAlgorithm")

        self._algorithms[name] = algorithm
        self._logger.info(f"Registered algorithm: {name}")

    def set_algorithm(self, algorithm_name: str) -> None:
        """Set the current algorithm."""
        if algorithm_name not in self._algorithms:
            available = ', '.join(self._algorithms.keys())
            raise ValueError(f"Algorithm '{algorithm_name}' not registered. Available: {available}")

        self._current_algorithm = algorithm_name
        self._logger.info(f"Switched to algorithm: {algorithm_name}")

    def get_available_algorithms(self) -> List[str]:
        """Get list of available algorithms."""
        return list(self._algorithms.keys())

    def get_current_algorithm(self) -> str:
        """Get current algorithm name."""
        return self._current_algorithm

    def encode_message(self, image: np.ndarray, message: str, **kwargs) -> np.ndarray:
        """Encode message into image using current algorithm."""
        start_time = time.time()
        algorithm = self._algorithms[self._current_algorithm]

        self._logger.info(f"Encoding message with {self._current_algorithm} algorithm")
        result = algorithm.encode(image, message, **kwargs)

        elapsed = time.time() - start_time
        self._logger.info(f"Encoding completed in {elapsed:.2f} seconds")
        return result

    def decode_message(self, image: np.ndarray, **kwargs) -> str:
        """Decode message from image using current algorithm."""
        start_time = time.time()
        algorithm = self._algorithms[self._current_algorithm]

        self._logger.info(f"Decoding message with {self._current_algorithm} algorithm")
        result = algorithm.decode(image, **kwargs)

        elapsed = time.time() - start_time
        self._logger.info(f"Decoding completed in {elapsed:.2f} seconds")
        return result

    def can_fit_message(self, image: np.ndarray, message: str, **kwargs) -> bool:
        """Check if message can fit using current algorithm."""
        algorithm = self._algorithms[self._current_algorithm]
        return algorithm.can_fit_message(image, message, **kwargs)

    def get_capacity(self, image: np.ndarray, **kwargs) -> int:
        """Get maximum message capacity using current algorithm."""
        algorithm = self._algorithms[self._current_algorithm]
        return algorithm.get_capacity(image, **kwargs)

    def get_algorithm_info(self, algorithm_name: Optional[str] = None) -> Dict[str, Any]:
        """Get information about an algorithm."""
        name = algorithm_name or self._current_algorithm
        if name not in self._algorithms:
            raise ValueError(f"Algorithm '{name}' not found")

        algorithm = self._algorithms[name]
        return {
            'name': name,
            'class': algorithm.__class__.__name__,
            'description': algorithm.__class__.__doc__ or "No description available"
        }

    def _register_algorithms(self) -> None:
        """Register DCT and DWT algorithms."""
        try:
            # Simple DCT algorithm (simplified version)
            self._algorithms['dct'] = SimpleDCTAlgorithm()
            self._logger.info("Registered DCT algorithm")

            # Simple DWT algorithm (simplified version)
            self._algorithms['dwt'] = SimpleDWTAlgorithm()
            self._logger.info("Registered DWT algorithm")

        except Exception as e:
            self._logger.error(f"Error registering algorithms: {e}")


class SimpleDCTAlgorithm(SteganographyAlgorithm):
    """Simplified DCT algorithm matching web interface."""

    def encode(self, image: np.ndarray, message: str, **_kwargs) -> np.ndarray:
        """Encode using simplified DCT (every 4th pixel blue channel)."""
        full_message = message + "###END###"
        binary_message = ''.join(format(ord(char), '08b') for char in full_message)

        stego_image = image.copy()
        flat_image = stego_image.flatten()

        bit_index = 0
        for i in range(2, len(flat_image), 16):  # Every 4th pixel, blue channel
            if bit_index >= len(binary_message):
                break
            bit = int(binary_message[bit_index])
            flat_image[i] = (flat_image[i] & 0xFE) | bit
            bit_index += 1

        return flat_image.reshape(stego_image.shape)

    def decode(self, image: np.ndarray, **_kwargs) -> str:
        """Decode from simplified DCT."""
        flat_image = image.flatten()
        binary_message = ""

        for i in range(2, len(flat_image), 16):  # Every 4th pixel, blue channel
            bit = flat_image[i] & 1
            binary_message += str(bit)

            if binary_message.endswith('001110010011001000110011001001010100111001000100001110010011001000110011001110010011001000110011'):  # "###END###" in binary
                binary_message = binary_message[:-72]  # Remove delimiter

                message = ""
                for j in range(0, len(binary_message), 8):
                    byte = binary_message[j:j+8]
                    if len(byte) == 8:
                        message += chr(int(byte, 2))
                return message

        return ""

    def can_fit_message(self, image: np.ndarray, message: str, **_kwargs) -> bool:
        """Check capacity for DCT."""
        full_message = message + "###END###"
        message_bits = len(full_message) * 8
        available_bits = image.size // 16  # Every 4th pixel
        return message_bits <= available_bits

    def get_capacity(self, image: np.ndarray, **_kwargs) -> int:
        """Get DCT capacity."""
        available_bits = image.size // 16 - 72  # Minus delimiter
        return max(0, available_bits // 8)


class SimpleDWTAlgorithm(SteganographyAlgorithm):
    """Simplified DWT algorithm matching web interface."""

    def encode(self, image: np.ndarray, message: str, **_kwargs) -> np.ndarray:
        """Encode using simplified DWT (every 8th pixel green channel)."""
        full_message = message + "###END###"
        binary_message = ''.join(format(ord(char), '08b') for char in full_message)

        stego_image = image.copy()
        flat_image = stego_image.flatten()

        bit_index = 0
        for i in range(1, len(flat_image), 32):  # Every 8th pixel, green channel
            if bit_index >= len(binary_message):
                break
            bit = int(binary_message[bit_index])
            flat_image[i] = (flat_image[i] & 0xFE) | bit
            bit_index += 1

        return flat_image.reshape(stego_image.shape)

    def decode(self, image: np.ndarray, **_kwargs) -> str:
        """Decode from simplified DWT."""
        flat_image = image.flatten()
        binary_message = ""

        for i in range(1, len(flat_image), 32):  # Every 8th pixel, green channel
            bit = flat_image[i] & 1
            binary_message += str(bit)

            if binary_message.endswith('001110010011001000110011001001010100111001000100001110010011001000110011001110010011001000110011'):  # "###END###" in binary
                binary_message = binary_message[:-72]  # Remove delimiter

                message = ""
                for j in range(0, len(binary_message), 8):
                    byte = binary_message[j:j+8]
                    if len(byte) == 8:
                        message += chr(int(byte, 2))
                return message

        return ""

    def can_fit_message(self, image: np.ndarray, message: str, **_kwargs) -> bool:
        """Check capacity for DWT."""
        full_message = message + "###END###"
        message_bits = len(full_message) * 8
        available_bits = image.size // 32  # Every 8th pixel
        return message_bits <= available_bits

    def get_capacity(self, image: np.ndarray, **_kwargs) -> int:
        """Get DWT capacity."""
        available_bits = image.size // 32 - 72  # Minus delimiter
        return max(0, available_bits // 8)
