"""
Progress indicators and status reporting utilities. 

Provides simple progress bars and status updates for CLI operations.
"""

import sys
import time
from typing import Optional


class ProgressBar:
    """Simple progress bar for CLI operations."""
    
    def __init__(self, total: int, description: str = "Processing", width: int = 50):
        self.total = total
        self.current = 0
        self.description = description
        self.width = width
        self.start_time = time.time()
        
    def update(self, increment: int = 1, status: Optional[str] = None):
        """Update progress bar."""
        self.current += increment
        if self.current > self.total:
            self.current = self.total
            
        # Calculate progress
        progress = self.current / self.total if self.total > 0 else 0
        filled_width = int(self.width * progress)
        
        # Create progress bar
        bar = "=" * filled_width + "-" * (self.width - filled_width)
        
        # Calculate time info
        elapsed = time.time() - self.start_time
        if progress > 0:
            eta = elapsed * (1 - progress) / progress
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"
        
        # Format output
        percent = progress * 100
        output = f"\r{self.description}: [{bar}] {percent:.1f}% ({self.current}/{self.total}) {eta_str}"
        
        if status:
            output += f" - {status}"
            
        # Print progress
        sys.stdout.write(output)
        sys.stdout.flush()
        
        # New line when complete
        if self.current >= self.total:
            print()
    
    def finish(self, message: str = "Complete"):
        """Finish progress bar with message."""
        self.current = self.total
        elapsed = time.time() - self.start_time
        print(f"\r{self.description}: {message} (took {elapsed:.1f}s)")


class Spinner:
    """Simple spinner for indeterminate progress."""
    
    def __init__(self, description: str = "Processing"):
        self.description = description
        self.chars = "|/-\\"
        self.index = 0
        self.running = False
        
    def start(self):
        """Start spinner."""
        self.running = True
        self._spin()
        
    def stop(self, message: str = "Done"):
        """Stop spinner with message."""
        self.running = False
        print(f"\r{self.description}: {message}")
        
    def _spin(self):
        """Spin the spinner."""
        if self.running:
            char = self.chars[self.index % len(self.chars)]
            sys.stdout.write(f"\r{self.description}: {char}")
            sys.stdout.flush()
            self.index += 1


class StatusReporter:
    """Status reporter for operations."""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.start_time = time.time()
        
    def info(self, message: str):
        """Print info message."""
        if self.verbose:
            print(f"INFO: {message}")
            
    def success(self, message: str):
        """Print success message."""
        if self.verbose:
            print(f"SUCCESS: {message}")
            
    def warning(self, message: str):
        """Print warning message."""
        if self.verbose:
            print(f"WARNING: {message}")
            
    def error(self, message: str):
        """Print error message."""
        if self.verbose:
            print(f"ERROR: {message}")
            
    def step(self, step_name: str):
        """Print step message."""
        if self.verbose:
            elapsed = time.time() - self.start_time
            print(f"[{elapsed:.1f}s] {step_name}")


def format_time(seconds: float) -> str:
    """Format time duration."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


def format_size(bytes_size: int) -> str:
    """Format file size."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024 # type: ignore
    return f"{bytes_size:.1f} TB"


# Context managers for easy use
class progress_bar:
    """Context manager for progress bar."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.bar = ProgressBar(total, description)
        
    def __enter__(self):
        return self.bar
        
    def __exit__(self, exc_type, *_args):  # type: ignore
        if exc_type is None:
            self.bar.finish()
        else:
            self.bar.finish("Failed")


class spinner:
    """Context manager for spinner."""
    
    def __init__(self, description: str = "Processing"):
        self.spinner = Spinner(description)
        
    def __enter__(self):
        self.spinner.start()
        return self.spinner
        
    def __exit__(self, exc_type, *_args):  # type: ignore
        if exc_type is None:
            self.spinner.stop("Done")
        else:
            self.spinner.stop("Failed")


# Example usage
if __name__ == "__main__":
    import time
    
    # Progress bar example
    print("Testing progress bar:")
    with progress_bar(100, "Encoding") as bar:
        for i in range(100):
            time.sleep(0.01)
            bar.update(1, f"Processing item {i+1}")
    
    # Spinner example
    print("\nTesting spinner:")
    with spinner("Loading"):
        time.sleep(2)
    
    # Status reporter example
    print("\nTesting status reporter:")
    reporter = StatusReporter()
    reporter.info("Starting operation")
    reporter.step("Step 1: Initialize")
    time.sleep(0.5)
    reporter.step("Step 2: Process")
    time.sleep(0.5)
    reporter.success("Operation completed")
