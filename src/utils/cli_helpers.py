"""
CLI helper utilities for enhanced user experience. 

Provides auto-completion, input validation, and user-friendly prompts.
"""

import os
import glob
from typing import List, Optional
from pathlib import Path


def get_image_files(directory: str = ".") -> List[str]:
    """Get list of image files in directory."""
    image_extensions = ["*.png", "*.bmp", "*.tiff", "*.tif", "*.jpg", "*.jpeg"]
    image_files = []
    
    for ext in image_extensions:
        pattern = os.path.join(directory, ext)
        image_files.extend(glob.glob(pattern))
        # Also check uppercase
        pattern = os.path.join(directory, ext.upper())
        image_files.extend(glob.glob(pattern))
    
    return sorted(image_files)


def get_audio_files(directory: str = ".") -> List[str]:
    """Get list of audio files in directory."""
    audio_extensions = ["*.wav", "*.flac", "*.aiff", "*.aif"]
    audio_files = []
    
    for ext in audio_extensions:
        pattern = os.path.join(directory, ext)
        audio_files.extend(glob.glob(pattern))
        # Also check uppercase
        pattern = os.path.join(directory, ext.upper())
        audio_files.extend(glob.glob(pattern))
    
    return sorted(audio_files)


def suggest_files(partial_path: str, file_type: str = "image") -> List[str]:
    """Suggest files based on partial path."""
    if file_type == "image":
        get_files_func = get_image_files
    elif file_type == "audio":
        get_files_func = get_audio_files
    else:
        # All files
        return glob.glob(partial_path + "*")
    
    # Get directory and filename parts
    directory = os.path.dirname(partial_path) or "."
    filename_part = os.path.basename(partial_path)
    
    # Get all files of the type
    all_files = get_files_func(directory)
    
    # Filter by filename part
    if filename_part:
        matching_files = [f for f in all_files if os.path.basename(f).startswith(filename_part)]
    else:
        matching_files = all_files
    
    return matching_files[:10]  # Limit to 10 suggestions


def prompt_for_file(prompt: str, file_type: str = "image", default: Optional[str] = None) -> Optional[str]:
    """Interactive file selection with suggestions."""
    print(f"\n{prompt}")
    
    if default:
        print(f"Default: {default}")
    
    # Show available files
    if file_type == "image":
        files = get_image_files()
        print(f"\nAvailable image files:")
    elif file_type == "audio":
        files = get_audio_files()
        print(f"\nAvailable audio files:")
    else:
        files = []
    
    if files:
        for i, file in enumerate(files[:10], 1):
            size = os.path.getsize(file)
            size_str = format_size(size)
            print(f"  {i}. {file} ({size_str})")
        
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")
    else:
        print("  No files found in current directory")
    
    while True:
        try:
            user_input = input(f"\nEnter file path (or number): ").strip()
            
            if not user_input and default:
                return default
            
            if not user_input:
                continue
            
            # Check if it's a number (file selection)
            if user_input.isdigit():
                index = int(user_input) - 1
                if 0 <= index < len(files):
                    return files[index]
                else:
                    print(f"Invalid selection. Please choose 1-{len(files)}")
                    continue
            
            # Check if file exists
            if os.path.exists(user_input):
                return user_input
            
            # Try to suggest files
            suggestions = suggest_files(user_input, file_type)
            if suggestions:
                print(f"\nDid you mean:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}")
                
                choice = input("Enter number or continue typing: ").strip()
                if choice.isdigit():
                    index = int(choice) - 1
                    if 0 <= index < len(suggestions):
                        return suggestions[index]
            
            print(f"File not found: {user_input}")
            
        except KeyboardInterrupt:
            print("\nCancelled")
            return None
        except EOFError:
            return None


def prompt_for_algorithm() -> str:
    """Interactive algorithm selection."""
    algorithms = {
        "1": ("lsb", "LSB (Least Significant Bit) - Fast, good capacity"),
        "2": ("dct", "DCT (Discrete Cosine Transform) - JPEG resistant"),
        "3": ("adaptive_lsb", "Adaptive LSB - Edge detection based"),
        "4": ("spectral", "Spectral - For audio files only")
    }
    
    print("\nAvailable algorithms:")
    for key, (name, description) in algorithms.items():
        print(f"  {key}. {name} - {description}")
    
    while True:
        try:
            choice = input("\nSelect algorithm (1-4, default: 1): ").strip()
            
            if not choice:
                return "lsb"
            
            if choice in algorithms:
                return algorithms[choice][0]
            
            print("Invalid choice. Please select 1-4.")
            
        except KeyboardInterrupt:
            print("\nCancelled")
            return "lsb"


def prompt_for_message() -> Optional[str]:
    """Interactive message input with validation."""
    print("\nEnter your secret message:")
    print("(Press Ctrl+C to cancel, Ctrl+D when done)")
    
    lines = []
    try:
        while True:
            try:
                line = input()
                lines.append(line)
            except EOFError:
                break
    except KeyboardInterrupt:
        print("\nCancelled")
        return None
    
    message = "\n".join(lines).strip()
    
    if not message:
        print("Empty message. Please enter some text.")
        return prompt_for_message()
    
    print(f"\nMessage length: {len(message)} characters")
    return message


def confirm_action(prompt: str, default: bool = False) -> bool:
    """Ask for user confirmation."""
    default_str = "Y/n" if default else "y/N"
    
    while True:
        try:
            response = input(f"{prompt} ({default_str}): ").strip().lower()
            
            if not response:
                return default
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")
                
        except KeyboardInterrupt:
            print("\nCancelled")
            return False


def format_size(size: int) -> str:
    """Format file size in human readable format."""
    bytes_size: float = float(size)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def print_file_info(file_path: str):
    """Print file information."""
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return
    
    stat = os.stat(file_path)
    size = format_size(stat.st_size)
    
    print(f"File: {file_path}")
    print(f"Size: {size}")
    print(f"Modified: {os.path.getmtime(file_path)}")


def create_output_filename(input_file: str, suffix: str = "_stego", extension: Optional[str] = None) -> str:
    """Create output filename based on input file."""
    path = Path(input_file)
    
    if extension is None:
        extension = path.suffix
    
    output_name = f"{path.stem}{suffix}{extension}"
    output_path = path.parent / output_name
    
    # Avoid overwriting existing files
    counter = 1
    while output_path.exists():
        output_name = f"{path.stem}{suffix}_{counter}{extension}"
        output_path = path.parent / output_name
        counter += 1
    
    return str(output_path)


def validate_output_path(output_path: str, input_path: str) -> bool:
    """Validate output path."""
    # Check if output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created directory: {output_dir}")
        except OSError as e:
            print(f"Cannot create directory {output_dir}: {e}")
            return False
    
    # Check if we're overwriting input file
    if os.path.abspath(output_path) == os.path.abspath(input_path):
        print("Error: Output file cannot be the same as input file")
        return False
    
    # Check if output file exists
    if os.path.exists(output_path):
        if not confirm_action(f"Output file exists: {output_path}. Overwrite?"):
            return False
    
    return True


# Interactive mode functions
def interactive_encode():
    """Interactive encoding mode."""
    print("=== Interactive Encoding Mode ===")
    
    # Get input file
    input_file = prompt_for_file("Select input image file:", "image")
    if not input_file:
        return
    
    print_file_info(input_file)
    
    # Get message
    message = prompt_for_message()
    if not message:
        return
    
    # Get algorithm
    algorithm = prompt_for_algorithm()
    
    # Get output file
    default_output = create_output_filename(input_file)
    output_file = input(f"Output file (default: {default_output}): ").strip()
    if not output_file:
        output_file = default_output
    
    if not validate_output_path(output_file, input_file):
        return
    
    # Get password
    use_password = confirm_action("Use password protection?")
    password = None
    if use_password:
        import getpass
        password = getpass.getpass("Enter password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        if password != confirm_password:
            print("Passwords don't match!")
            return
    
    print(f"\nConfiguration:")
    print(f"  Input: {input_file}")
    print(f"  Output: {output_file}")
    print(f"  Algorithm: {algorithm}")
    print(f"  Message length: {len(message)} characters")
    print(f"  Password protected: {'Yes' if password else 'No'}")
    
    if not confirm_action("Proceed with encoding?", True):
        return
    
    return {
        'input': input_file,
        'output': output_file,
        'message': message,
        'algorithm': algorithm,
        'password': password
    }


def interactive_decode():
    """Interactive decoding mode."""
    print("=== Interactive Decoding Mode ===")
    
    # Get input file
    input_file = prompt_for_file("Select steganographic image file:", "image")
    if not input_file:
        return
    
    print_file_info(input_file)
    
    # Get algorithm
    algorithm = prompt_for_algorithm()
    
    # Get password
    use_password = confirm_action("Is the message password protected?")
    password = None
    if use_password:
        import getpass
        password = getpass.getpass("Enter password: ")
    
    print(f"\nConfiguration:")
    print(f"  Input: {input_file}")
    print(f"  Algorithm: {algorithm}")
    print(f"  Password protected: {'Yes' if password else 'No'}")
    
    if not confirm_action("Proceed with decoding?", True):
        return
    
    return {
        'input': input_file,
        'algorithm': algorithm,
        'password': password
    }
