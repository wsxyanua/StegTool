"""Helper utilities for common operations."""

import os
import threading
import time
from typing import Callable, Optional


class ProgressTracker:
    """Simple progress tracking utility."""
    
    def __init__(self, total_steps: int, callback: Optional[Callable] = None):
        # Input validation
        if total_steps <= 0:
            raise ValueError("Total steps must be positive")
        
        self.total_steps = total_steps
        self.current_step = 0
        self.callback = callback
        self.start_time = time.time()
        self.lock = threading.Lock()
    
    def update(self, step: Optional[int] = None, message: str = ""):
        """Update progress."""
        with self.lock:
            if step is not None:
                if step < 0 or step > self.total_steps:
                    raise ValueError(f"Step must be between 0 and {self.total_steps}")
                self.current_step = step
            else:
                self.current_step += 1
            
            progress = min(100.0, (self.current_step / self.total_steps) * 100)
            elapsed = time.time() - self.start_time
            
            if self.callback:
                self.callback(progress, message, elapsed)
    
    def finish(self, message: str = "Complete"):
        """Mark as finished."""
        self.update(self.total_steps, message)
    
    def reset(self):
        """Reset progress."""
        with self.lock:
            self.current_step = 0
            self.start_time = time.time()


def safe_filename(filename: str) -> str:
    """Create a safe filename by removing invalid characters."""
    import re
    
    # Input validation
    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")
    
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(safe_name) > 100:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:90] + ext
    return safe_name


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    # Input validation
    if size_bytes < 0:
        raise ValueError("File size cannot be negative")

    size_float = float(size_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_float < 1024.0:
            return f"{size_float:.1f} {unit}"
        size_float /= 1024.0
    return f"{size_float:.1f} TB"

