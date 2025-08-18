""" Image processing utilities. """

import numpy as np
from PIL import Image
from typing import Optional, Tuple
import os


class ImageHandler:
    """Handles image loading, saving, and basic processing."""
    
    SUPPORTED_FORMATS = {'.png', '.bmp', '.tiff', '.tga'}
    
    @classmethod
    def load_image(cls, file_path: str) -> Tuple[np.ndarray, dict]:
        """
        Load image from file.
        
        Args:
            file_path: Path to image file
            
        Returns:
            Tuple of (image_array, metadata)
        """
        # Input validation
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")
        
        if not os.path.exists(file_path):
            raise ValueError(f"File does not exist: {file_path}")
        
        try:
            pil_image = Image.open(file_path)
            
            # Convert to RGB if necessary (handle RGBA, grayscale, etc.)
            if pil_image.mode not in ['RGB', 'L']:
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array
            image_array = np.array(pil_image)
            
            # Metadata
            metadata = {
                'original_mode': pil_image.mode,
                'size': pil_image.size,
                'format': pil_image.format,
                'filename': file_path
            }
            
            return image_array, metadata
            
        except Exception as e:
            raise ValueError(f"Error loading image: {str(e)}")
    
    @classmethod
    def save_image(cls, image_array: np.ndarray, file_path: str, 
                   metadata: Optional[dict] = None) -> bool:
        """
        Save image array to file.
        
        Args:
            image_array: Image as numpy array
            file_path: Output file path
            metadata: Optional metadata from original image
            
        Returns:
            True if successful
        """
        # Input validation
        if image_array is None or image_array.size == 0:
            raise ValueError("Image array cannot be empty or None")
        
        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")
        
        try:
            # Convert numpy array to PIL Image
            if len(image_array.shape) == 2:  # Grayscale
                pil_image = Image.fromarray(image_array, mode='L')
            else:  # RGB
                pil_image = Image.fromarray(image_array, mode='RGB')
            
            # Save with lossless compression for supported formats
            if file_path.lower().endswith('.png'):
                pil_image.save(file_path, 'PNG', compress_level=1)
            elif file_path.lower().endswith('.bmp'):
                pil_image.save(file_path, 'BMP')
            elif file_path.lower().endswith(('.tiff', '.tif')):
                pil_image.save(file_path, 'TIFF', compression='lzw')
            else:
                pil_image.save(file_path)
            
            return True
            
        except Exception as e:
            raise ValueError(f"Error saving image: {str(e)}")
    
    @classmethod
    def is_supported_format(cls, file_path: str) -> bool:
        """Check if file format is supported for steganography."""
        extension = file_path.lower().split('.')[-1]
        return f'.{extension}' in cls.SUPPORTED_FORMATS
    
    @classmethod
    def get_image_info(cls, image_array: np.ndarray) -> dict:
        """Get basic information about image."""
        info = {
            'shape': image_array.shape,
            'dtype': str(image_array.dtype),
            'size_bytes': image_array.nbytes,
            'max_message_length': image_array.size // 8  # Rough estimate for LSB
        }
        
        if len(image_array.shape) == 3:
            info['channels'] = image_array.shape[2]
            info['width'] = image_array.shape[1]
            info['height'] = image_array.shape[0]
        elif len(image_array.shape) == 2:
            info['channels'] = 1
            info['width'] = image_array.shape[1]
            info['height'] = image_array.shape[0]
        else:
            # 1D array case
            info['channels'] = 1
            info['width'] = image_array.shape[0]
            info['height'] = 1
        
        return info
