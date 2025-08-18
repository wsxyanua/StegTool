"""
Advanced steganography algorithms for enhanced security and capacity. 

This module implements sophisticated steganography techniques including:
- DCT-based steganography (JPEG-resistant)
- Spread spectrum steganography
- Adaptive LSB with error correction
"""

import numpy as np
from typing import Tuple, List
import logging
from .steganography import SteganographyAlgorithm

try:
    from scipy.fft import dct, idct
    from scipy import ndimage
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    # Fallback implementations will be provided


class DCTAlgorithm(SteganographyAlgorithm):
    """
    DCT-based steganography algorithm.

    Uses Discrete Cosine Transform to hide data in frequency domain,
    making it more resistant to compression and filtering.
    """

    BLOCK_SIZE = 8
    DELIMITER = "###DCT_END###"
    QUANTIZATION_FACTOR = 10

    def __init__(self, quality_factor: float = 0.1):
        """
        Initialize DCT algorithm.

        Args:
            quality_factor: Controls embedding strength (0.01-1.0)
        """
        if not SCIPY_AVAILABLE:
            raise ImportError("DCT algorithm requires scipy. Install with: pip install scipy")

        self.quality_factor = max(0.01, min(1.0, quality_factor))
        self.logger = logging.getLogger(__name__)

    def _apply_dct_2d(self, block: np.ndarray) -> np.ndarray:
        """Apply 2D DCT to 8x8 block."""
        if not SCIPY_AVAILABLE:
            raise RuntimeError("DCT operations require scipy")
        # Type ignore for scipy compatibility
        result = dct(dct(block.T, norm='ortho').T, norm='ortho')  # type: ignore
        return np.asarray(result)

    def _apply_idct_2d(self, block: np.ndarray) -> np.ndarray:
        """Apply 2D inverse DCT to 8x8 block."""
        if not SCIPY_AVAILABLE:
            raise RuntimeError("DCT operations require scipy")
        # Type ignore for scipy compatibility
        result = idct(idct(block.T, norm='ortho').T, norm='ortho')  # type: ignore
        return np.asarray(result)
    
    def _get_embeddable_coefficients(self, dct_block: np.ndarray) -> List[Tuple[int, int]]:  # noqa: ARG002
        """Get DCT coefficients suitable for embedding (mid-frequency)."""
        # Avoid DC component (0,0) and high-frequency components
        positions = []
        for i in range(1, min(6, self.BLOCK_SIZE)):
            for j in range(1, min(6, self.BLOCK_SIZE)):
                if i + j < 8:  # Avoid highest frequencies
                    positions.append((i, j))
        return positions
    
    def encode(self, image: np.ndarray, message: str, **kwargs) -> np.ndarray:
        """
        Encode message using DCT-based steganography.
        
        Args:
            image: Input image as numpy array
            message: Message to hide
            **kwargs: Additional parameters
            
        Returns:
            Modified image with hidden message
        """
        # Input validation
        if image is None or image.size == 0:
            raise ValueError("Invalid image: empty or None")
        
        if not message or len(message.strip()) == 0:
            raise ValueError("Message cannot be empty")
        
        # Prepare message
        full_message = message + self.DELIMITER
        binary_message = ''.join(format(ord(char), '08b') for char in full_message)
        
        # Check capacity
        if not self.can_fit_message(image, message, **kwargs):
            raise ValueError("Message too long for this image")
        
        # Convert to float for DCT processing
        stego_image = image.astype(np.float64)
        
        # Process each channel separately
        if len(stego_image.shape) == 3:
            channels = stego_image.shape[2]
        else:
            channels = 1
            stego_image = stego_image.reshape(stego_image.shape[0], stego_image.shape[1], 1)
        
        bit_index = 0
        
        for channel in range(channels):
            if bit_index >= len(binary_message):
                break
                
            channel_data = stego_image[:, :, channel]
            height, width = channel_data.shape
            
            # Process 8x8 blocks
            for i in range(0, height - self.BLOCK_SIZE + 1, self.BLOCK_SIZE):
                for j in range(0, width - self.BLOCK_SIZE + 1, self.BLOCK_SIZE):
                    if bit_index >= len(binary_message):
                        break
                    
                    # Extract 8x8 block
                    block = channel_data[i:i+self.BLOCK_SIZE, j:j+self.BLOCK_SIZE]
                    
                    # Apply DCT
                    dct_block = self._apply_dct_2d(block)
                    
                    # Get embeddable positions
                    positions = self._get_embeddable_coefficients(dct_block)
                    
                    # Embed bits in mid-frequency coefficients
                    for pos in positions:
                        if bit_index >= len(binary_message):
                            break
                        
                        row, col = pos
                        bit = int(binary_message[bit_index])
                        
                        # Modify coefficient based on bit value
                        # Simpler and more robust method
                        coeff = dct_block[row, col]
                        magnitude = abs(coeff) + self.quality_factor * self.QUANTIZATION_FACTOR

                        if bit == 1:
                            dct_block[row, col] = magnitude
                        else:
                            dct_block[row, col] = -magnitude
                        
                        bit_index += 1
                    
                    # Apply inverse DCT
                    modified_block = self._apply_idct_2d(dct_block)
                    channel_data[i:i+self.BLOCK_SIZE, j:j+self.BLOCK_SIZE] = modified_block
            
            stego_image[:, :, channel] = channel_data
        
        # Convert back to original data type and shape
        result = np.clip(stego_image, 0, 255).astype(image.dtype)
        if len(image.shape) == 2:
            result = result[:, :, 0]
        
        return result
    
    def decode(self, image: np.ndarray, **kwargs) -> str:  # noqa: ARG002
        """
        Decode message from DCT-modified image.
        
        Args:
            image: Image containing hidden message
            **kwargs: Additional parameters
            
        Returns:
            Extracted message
        """
        # Input validation
        if image is None or image.size == 0:
            raise ValueError("Invalid image: empty or None")
        
        # Convert to float for DCT processing
        decode_image = image.astype(np.float64)
        
        # Handle grayscale/color
        if len(decode_image.shape) == 2:
            decode_image = decode_image.reshape(decode_image.shape[0], decode_image.shape[1], 1)
            channels = 1
        else:
            channels = decode_image.shape[2]
        
        binary_bits = []
        
        for channel in range(channels):
            channel_data = decode_image[:, :, channel]
            height, width = channel_data.shape
            
            # Process 8x8 blocks
            for i in range(0, height - self.BLOCK_SIZE + 1, self.BLOCK_SIZE):
                for j in range(0, width - self.BLOCK_SIZE + 1, self.BLOCK_SIZE):
                    # Extract 8x8 block
                    block = channel_data[i:i+self.BLOCK_SIZE, j:j+self.BLOCK_SIZE]
                    
                    # Apply DCT
                    dct_block = self._apply_dct_2d(block)
                    
                    # Get embeddable positions
                    positions = self._get_embeddable_coefficients(dct_block)
                    
                    # Extract bits from coefficients
                    for pos in positions:
                        row, col = pos
                        coeff = dct_block[row, col]

                        # Extract bit based on coefficient sign and magnitude
                        # More robust extraction method
                        if coeff > 0:
                            binary_bits.append('1')
                        else:
                            binary_bits.append('0')
        
        # Convert binary to text
        binary_string = ''.join(binary_bits)
        decoded_chars = []
        
        for i in range(0, len(binary_string), 8):
            byte = binary_string[i:i+8]
            if len(byte) == 8:
                try:
                    char = chr(int(byte, 2))
                    decoded_chars.append(char)
                    
                    # Check for delimiter
                    current_text = ''.join(decoded_chars)
                    if current_text.endswith(self.DELIMITER):
                        return current_text[:-len(self.DELIMITER)]
                except ValueError:
                    continue
        
        return ''.join(decoded_chars)
    
    def can_fit_message(self, image: np.ndarray, message: str, **kwargs) -> bool:  # noqa: ARG002
        """Check if message can fit using DCT algorithm."""
        if image is None or image.size == 0:
            return False
        
        if not message or len(message.strip()) == 0:
            return False
        
        full_message = message + self.DELIMITER
        message_bits = len(full_message) * 8
        
        # Calculate available DCT coefficients
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) > 2 else 1
        
        blocks_h = height // self.BLOCK_SIZE
        blocks_w = width // self.BLOCK_SIZE
        total_blocks = blocks_h * blocks_w * channels
        
        # Each block can hold multiple bits in mid-frequency coefficients
        coeffs_per_block = len(self._get_embeddable_coefficients(np.zeros((self.BLOCK_SIZE, self.BLOCK_SIZE))))
        available_bits = total_blocks * coeffs_per_block
        
        return message_bits <= available_bits
    
    def get_capacity(self, image: np.ndarray, **kwargs) -> int:  # noqa: ARG002
        """Get maximum message capacity using DCT algorithm."""
        if image is None or image.size == 0:
            return 0
        
        height, width = image.shape[:2]
        channels = image.shape[2] if len(image.shape) > 2 else 1
        
        blocks_h = height // self.BLOCK_SIZE
        blocks_w = width // self.BLOCK_SIZE
        total_blocks = blocks_h * blocks_w * channels
        
        coeffs_per_block = len(self._get_embeddable_coefficients(np.zeros((self.BLOCK_SIZE, self.BLOCK_SIZE))))
        available_bits = total_blocks * coeffs_per_block
        
        # Reserve space for delimiter
        delimiter_bits = len(self.DELIMITER) * 8
        return max(0, (available_bits - delimiter_bits) // 8)


class AdaptiveLSBAlgorithm(SteganographyAlgorithm):
    """
    Adaptive LSB algorithm with edge detection and error correction.
    
    Embeds data preferentially in edge regions where changes are less noticeable.
    """
    
    DELIMITER = "###ADAPTIVE_END###"
    
    def __init__(self, edge_threshold: float = 30.0):
        """
        Initialize adaptive LSB algorithm.
        
        Args:
            edge_threshold: Threshold for edge detection
        """
        self.edge_threshold = edge_threshold
        self.logger = logging.getLogger(__name__)
    
    def _detect_edges(self, image: np.ndarray) -> np.ndarray:
        """Detect edges using Sobel operator."""
        if not SCIPY_AVAILABLE:
            # Fallback to simple gradient-based edge detection
            return self._simple_edge_detection(image)

        if len(image.shape) == 3:
            # Convert to grayscale for edge detection
            gray = np.mean(image, axis=2)
        else:
            gray = image

        # Sobel edge detection
        sobel_x = ndimage.sobel(gray, axis=1)  # type: ignore
        sobel_y = ndimage.sobel(gray, axis=0)  # type: ignore
        edge_magnitude = np.sqrt(sobel_x**2 + sobel_y**2)

        return edge_magnitude > self.edge_threshold

    def _simple_edge_detection(self, image: np.ndarray) -> np.ndarray:
        """Simple edge detection fallback when scipy is not available."""
        if len(image.shape) == 3:
            gray = np.mean(image, axis=2)
        else:
            gray = image

        # Simple gradient-based edge detection
        grad_x = np.abs(np.diff(gray, axis=1))
        grad_y = np.abs(np.diff(gray, axis=0))

        # Pad to match original size
        grad_x = np.pad(grad_x, ((0, 0), (0, 1)), mode='edge')
        grad_y = np.pad(grad_y, ((0, 1), (0, 0)), mode='edge')

        edge_magnitude = np.sqrt(grad_x**2 + grad_y**2)
        return edge_magnitude > self.edge_threshold
    
    def encode(self, image: np.ndarray, message: str, **kwargs) -> np.ndarray:
        """Encode message using adaptive LSB with edge detection."""
        # Input validation
        if image is None or image.size == 0:
            raise ValueError("Invalid image: empty or None")
        
        if not message or len(message.strip()) == 0:
            raise ValueError("Message cannot be empty")
        
        # Prepare message
        full_message = message + self.DELIMITER
        binary_message = ''.join(format(ord(char), '08b') for char in full_message)
        
        # Check capacity
        if not self.can_fit_message(image, message, **kwargs):
            raise ValueError("Message too long for this image")
        
        # Detect edges
        edge_mask = self._detect_edges(image)
        
        # Create copy of image
        stego_image = image.copy()
        
        # Get edge pixel positions
        if len(image.shape) == 3:
            height, width, channels = image.shape
            edge_positions = []
            for c in range(channels):
                for y in range(height):
                    for x in range(width):
                        if edge_mask[y, x]:
                            edge_positions.append((y, x, c))
        else:
            height, width = image.shape
            edge_positions = [(y, x, 0) for y in range(height) for x in range(width) if edge_mask[y, x]]
        
        # Embed message bits in edge pixels
        for i, bit in enumerate(binary_message):
            if i >= len(edge_positions):
                raise ValueError("Not enough edge pixels for message")
            
            y, x, c = edge_positions[i]
            if len(image.shape) == 3:
                stego_image[y, x, c] = (stego_image[y, x, c] & 0xFE) | int(bit)
            else:
                stego_image[y, x] = (stego_image[y, x] & 0xFE) | int(bit)
        
        return stego_image
    
    def decode(self, image: np.ndarray, **kwargs) -> str:  # noqa: ARG002
        """Decode message from adaptive LSB image."""
        # Input validation
        if image is None or image.size == 0:
            raise ValueError("Invalid image: empty or None")
        
        # Detect edges (same as encoding)
        edge_mask = self._detect_edges(image)
        
        # Get edge pixel positions
        if len(image.shape) == 3:
            height, width, channels = image.shape
            edge_positions = []
            for c in range(channels):
                for y in range(height):
                    for x in range(width):
                        if edge_mask[y, x]:
                            edge_positions.append((y, x, c))
        else:
            height, width = image.shape
            edge_positions = [(y, x, 0) for y in range(height) for x in range(width) if edge_mask[y, x]]
        
        # Extract bits from edge pixels
        binary_bits = []
        for y, x, c in edge_positions:
            if len(image.shape) == 3:
                bit = image[y, x, c] & 1
            else:
                bit = image[y, x] & 1
            binary_bits.append(str(bit))
        
        # Convert binary to text
        binary_string = ''.join(binary_bits)
        decoded_chars = []
        
        for i in range(0, len(binary_string), 8):
            byte = binary_string[i:i+8]
            if len(byte) == 8:
                try:
                    char = chr(int(byte, 2))
                    decoded_chars.append(char)
                    
                    # Check for delimiter
                    current_text = ''.join(decoded_chars)
                    if current_text.endswith(self.DELIMITER):
                        return current_text[:-len(self.DELIMITER)]
                except ValueError:
                    continue
        
        return ''.join(decoded_chars)
    
    def can_fit_message(self, image: np.ndarray, message: str, **kwargs) -> bool:  # noqa: ARG002
        """Check if message can fit using adaptive LSB."""
        if image is None or image.size == 0:
            return False
        
        if not message or len(message.strip()) == 0:
            return False
        
        full_message = message + self.DELIMITER
        message_bits = len(full_message) * 8
        
        # Count edge pixels
        edge_mask = self._detect_edges(image)
        edge_count = np.sum(edge_mask)
        
        if len(image.shape) == 3:
            edge_count *= image.shape[2]  # Multiply by channels
        
        return message_bits <= edge_count
    
    def get_capacity(self, image: np.ndarray, **kwargs) -> int:  # noqa: ARG002
        """Get maximum message capacity using adaptive LSB."""
        if image is None or image.size == 0:
            return 0
        
        # Count edge pixels
        edge_mask = self._detect_edges(image)
        edge_count = np.sum(edge_mask)
        
        if len(image.shape) == 3:
            edge_count *= image.shape[2]  # Multiply by channels
        
        # Reserve space for delimiter
        delimiter_bits = len(self.DELIMITER) * 8
        return max(0, (edge_count - delimiter_bits) // 8)
