"""
Batch processing utilities for steganography operations. 

Provides functionality for processing multiple files, automated workflows,
and parallel processing capabilities.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..core.steganography import SteganographyEngine
from ..core.text_handler import TextHandler
from ..core.image_handler import ImageHandler
from ..utils.validators import FileValidator
from ..utils.helpers import ProgressTracker


class BatchProcessor:
    """Handles batch processing of steganography operations."""
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize batch processor.
        
        Args:
            max_workers: Maximum number of worker threads
        """
        self.max_workers = max_workers
        self.engine = SteganographyEngine()
        self.text_handler = TextHandler()
        self.logger = logging.getLogger(__name__)
        
    def batch_encode(self, 
                    input_dir: str,
                    output_dir: str,
                    message: str,
                    password: Optional[str] = None,
                    algorithm: str = 'lsb',
                    progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Batch encode message into multiple images.
        
        Args:
            input_dir: Directory containing input images
            output_dir: Directory for output images
            message: Message to hide in all images
            password: Optional password for encryption
            algorithm: Steganography algorithm to use
            progress_callback: Optional progress callback function
            
        Returns:
            Dictionary with processing results
        """
        # Validate inputs
        if not os.path.exists(input_dir):
            raise ValueError(f"Input directory not found: {input_dir}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all supported image files
        image_files = self._find_image_files(input_dir)
        if not image_files:
            raise ValueError(f"No supported image files found in {input_dir}")
        
        self.logger.info(f"Found {len(image_files)} image files for batch encoding")
        
        # Set algorithm
        self.engine.set_algorithm(algorithm)
        
        # Prepare message
        if password:
            processed_message = self.text_handler.prepare_message(message, password)
        else:
            processed_message = message
        
        # Setup progress tracking
        progress = ProgressTracker(len(image_files), progress_callback)
        results = {
            'total_files': len(image_files),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'processed_files': []
        }
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(
                    self._encode_single_file,
                    file_path,
                    output_dir,
                    processed_message,
                    algorithm
                ): file_path for file_path in image_files
            }
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['successful'] += 1
                        results['processed_files'].append(result)
                        self.logger.info(f"✓ Encoded: {os.path.basename(file_path)}")
                    else:
                        results['failed'] += 1
                        results['errors'].append(result)
                        self.logger.error(f"✗ Failed: {os.path.basename(file_path)} - {result['error']}")
                        
                except Exception as e:
                    results['failed'] += 1
                    error_result = {
                        'file': file_path,
                        'success': False,
                        'error': str(e)
                    }
                    results['errors'].append(error_result)
                    self.logger.error(f"✗ Exception: {os.path.basename(file_path)} - {str(e)}")
                
                # Update progress
                progress.update(message=f"Processed {results['successful'] + results['failed']}/{len(image_files)}")
        
        progress.finish("Batch encoding completed")
        
        # Log summary
        self.logger.info(f"Batch encoding completed: {results['successful']} successful, {results['failed']} failed")
        
        return results
    
    def batch_decode(self,
                    input_dir: str,
                    output_dir: str,
                    password: Optional[str] = None,
                    algorithm: str = 'lsb',
                    progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        Batch decode messages from multiple images.
        
        Args:
            input_dir: Directory containing images with hidden messages
            output_dir: Directory for decoded message files
            password: Optional password for decryption
            algorithm: Steganography algorithm to use
            progress_callback: Optional progress callback function
            
        Returns:
            Dictionary with processing results
        """
        # Validate inputs
        if not os.path.exists(input_dir):
            raise ValueError(f"Input directory not found: {input_dir}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Find all supported image files
        image_files = self._find_image_files(input_dir)
        if not image_files:
            raise ValueError(f"No supported image files found in {input_dir}")
        
        self.logger.info(f"Found {len(image_files)} image files for batch decoding")
        
        # Set algorithm
        self.engine.set_algorithm(algorithm)
        
        # Setup progress tracking
        progress = ProgressTracker(len(image_files), progress_callback)
        results = {
            'total_files': len(image_files),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'decoded_messages': []
        }
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_file = {
                executor.submit(
                    self._decode_single_file,
                    file_path,
                    output_dir,
                    password,
                    algorithm
                ): file_path for file_path in image_files
            }
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    result = future.result()
                    if result['success']:
                        results['successful'] += 1
                        results['decoded_messages'].append(result)
                        self.logger.info(f"✓ Decoded: {os.path.basename(file_path)}")
                    else:
                        results['failed'] += 1
                        results['errors'].append(result)
                        self.logger.warning(f"⚠ No message: {os.path.basename(file_path)}")
                        
                except Exception as e:
                    results['failed'] += 1
                    error_result = {
                        'file': file_path,
                        'success': False,
                        'error': str(e)
                    }
                    results['errors'].append(error_result)
                    self.logger.error(f"✗ Exception: {os.path.basename(file_path)} - {str(e)}")
                
                # Update progress
                progress.update(message=f"Processed {results['successful'] + results['failed']}/{len(image_files)}")
        
        progress.finish("Batch decoding completed")
        
        # Log summary
        self.logger.info(f"Batch decoding completed: {results['successful']} successful, {results['failed']} failed")
        
        return results
    
    def _find_image_files(self, directory: str) -> List[str]:
        """Find all supported image files in directory."""
        supported_extensions = FileValidator.get_supported_formats()
        image_files = []
        
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file.lower())
                if ext in supported_extensions:
                    # Validate file
                    is_valid, _ = FileValidator.validate_image_file(file_path)
                    if is_valid:
                        image_files.append(file_path)
        
        return sorted(image_files)
    
    def _encode_single_file(self, 
                           input_path: str,
                           output_dir: str,
                           message: str,
                           algorithm: str) -> Dict[str, Any]:
        """Encode message into single file."""
        try:
            # Load image
            image_array, metadata = ImageHandler.load_image(input_path)
            
            # Check capacity
            if not self.engine.can_fit_message(image_array, message):
                return {
                    'file': input_path,
                    'success': False,
                    'error': 'Message too long for image'
                }
            
            # Encode message
            stego_image = self.engine.encode_message(image_array, message)
            
            # Generate output path
            input_name = os.path.basename(input_path)
            name, ext = os.path.splitext(input_name)
            output_path = os.path.join(output_dir, f"{name}_stego{ext}")
            
            # Save result
            ImageHandler.save_image(stego_image, output_path, metadata)
            
            return {
                'file': input_path,
                'output': output_path,
                'success': True,
                'algorithm': algorithm,
                'message_length': len(message)
            }
            
        except Exception as e:
            return {
                'file': input_path,
                'success': False,
                'error': str(e)
            }
    
    def _decode_single_file(self,
                           input_path: str,
                           output_dir: str,
                           password: Optional[str],
                           algorithm: str) -> Dict[str, Any]:
        """Decode message from single file."""
        try:
            # Load image
            image_array, _ = ImageHandler.load_image(input_path)
            
            # Decode message
            encoded_message = self.engine.decode_message(image_array)
            
            if not encoded_message:
                return {
                    'file': input_path,
                    'success': False,
                    'error': 'No message found'
                }
            
            # Process decoded message
            if password:
                try:
                    message = self.text_handler.process_decoded_message(encoded_message, password)
                except ValueError:
                    return {
                        'file': input_path,
                        'success': False,
                        'error': 'Decryption failed - wrong password or corrupted data'
                    }
            else:
                message = encoded_message
            
            # Generate output path
            input_name = os.path.basename(input_path)
            name, _ = os.path.splitext(input_name)
            output_path = os.path.join(output_dir, f"{name}_decoded.txt")
            
            # Save decoded message
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(message)
            
            return {
                'file': input_path,
                'output': output_path,
                'success': True,
                'algorithm': algorithm,
                'message_length': len(message),
                'message_preview': message[:100] + '...' if len(message) > 100 else message
            }
            
        except Exception as e:
            return {
                'file': input_path,
                'success': False,
                'error': str(e)
            }
    
    def save_batch_report(self, results: Dict[str, Any], report_path: str) -> None:
        """Save batch processing report to JSON file."""
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Batch report saved to: {report_path}")
        except Exception as e:
            self.logger.error(f"Failed to save batch report: {str(e)}")


class WorkflowManager:
    """Manages automated steganography workflows."""
    
    def __init__(self):
        self.batch_processor = BatchProcessor()
        self.logger = logging.getLogger(__name__)
    
    def create_workflow_config(self, config_path: str) -> None:
        """Create a sample workflow configuration file."""
        sample_config = {
            "workflows": [
                {
                    "name": "batch_encode_workflow",
                    "type": "encode",
                    "input_dir": "./input_images",
                    "output_dir": "./encoded_images",
                    "message": "Default secret message",
                    "password": "optional_password",
                    "algorithm": "lsb",
                    "enabled": True
                },
                {
                    "name": "batch_decode_workflow", 
                    "type": "decode",
                    "input_dir": "./encoded_images",
                    "output_dir": "./decoded_messages",
                    "password": "optional_password",
                    "algorithm": "lsb",
                    "enabled": True
                }
            ]
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2)
        
        self.logger.info(f"Sample workflow config created: {config_path}")
    
    def run_workflow_from_config(self, config_path: str) -> Dict[str, Any]:
        """Run workflows from configuration file."""
        if not os.path.exists(config_path):
            raise ValueError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        results = {}
        
        for workflow in config.get('workflows', []):
            if not workflow.get('enabled', True):
                continue
            
            workflow_name = workflow['name']
            workflow_type = workflow['type']
            
            self.logger.info(f"Running workflow: {workflow_name}")
            
            try:
                if workflow_type == 'encode':
                    result = self.batch_processor.batch_encode(
                        input_dir=workflow['input_dir'],
                        output_dir=workflow['output_dir'],
                        message=workflow['message'],
                        password=workflow.get('password'),
                        algorithm=workflow.get('algorithm', 'lsb')
                    )
                elif workflow_type == 'decode':
                    result = self.batch_processor.batch_decode(
                        input_dir=workflow['input_dir'],
                        output_dir=workflow['output_dir'],
                        password=workflow.get('password'),
                        algorithm=workflow.get('algorithm', 'lsb')
                    )
                else:
                    raise ValueError(f"Unknown workflow type: {workflow_type}")
                
                results[workflow_name] = result
                self.logger.info(f"✓ Workflow completed: {workflow_name}")
                
            except Exception as e:
                results[workflow_name] = {
                    'success': False,
                    'error': str(e)
                }
                self.logger.error(f"✗ Workflow failed: {workflow_name} - {str(e)}")
        
        return results
