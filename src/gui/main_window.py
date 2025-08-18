""" Main GUI window for steganography tool. """

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import ImageTk
import threading
from typing import Optional, Dict, Any
import os
import json
import numpy as np

# Import core modules
from src.core.steganography import SteganographyEngine
from src.core.image_handler import ImageHandler
from src.core.text_handler import TextHandler


class SteganographyGUI:
    """Main GUI class for the steganography tool."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Steganography v1.0")
        self.root.geometry("800x600")
        self.root.minsize(600, 500)

        # Initialize core components
        self.engine = SteganographyEngine()
        self.text_handler = TextHandler()
        self.current_image: Optional[np.ndarray] = None
        self.current_image_metadata: Optional[Dict[str, Any]] = None
        self.preview_image: Optional[ImageTk.PhotoImage] = None
        self.settings_file = "gui_settings.json"
        self.recent_files = self._load_recent_files()
        self.settings = self._load_settings()
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        self.create_menu()

        # Restore settings
        self._restore_settings()

        # Bind close event to save settings
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
    def setup_styles(self):
        """Setup custom styles for the GUI."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom button style
        style.configure("Action.TButton", font=('Arial', 10, 'bold'))
        
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Load Image", command=self.load_image)
        file_menu.add_command(label="Save Result", command=self.save_result)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Image Info", command=self.show_image_info)
        tools_menu.add_command(label="Algorithm Settings", command=self.show_algorithm_settings)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Usage Guide", command=self.show_usage_guide)
    
    def create_widgets(self):
        """Create main GUI widgets."""
        # Create main notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Encode tab
        self.encode_frame = ttk.Frame(notebook)
        notebook.add(self.encode_frame, text="Hide Message")
        self.create_encode_widgets()
        
        # Decode tab
        self.decode_frame = ttk.Frame(notebook)
        notebook.add(self.decode_frame, text="Extract Message")
        self.create_decode_widgets()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                              relief='sunken', anchor='w')
        status_bar.pack(side='bottom', fill='x')
    
    def create_encode_widgets(self):
        """Create widgets for encoding tab."""
        # Image selection frame
        image_frame = ttk.LabelFrame(self.encode_frame, text="Select Image", padding=10)
        image_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(image_frame, text="Browse Image", 
                  command=self.load_image).pack(side='left')
        
        self.image_path_var = tk.StringVar()
        ttk.Label(image_frame, textvariable=self.image_path_var).pack(side='left', padx=(10, 0))
        
        # Message input frame
        msg_frame = ttk.LabelFrame(self.encode_frame, text="Message to Hide", padding=10)
        msg_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.message_text = scrolledtext.ScrolledText(msg_frame, height=8, wrap='word')
        self.message_text.pack(fill='both', expand=True)
        
        # Options frame
        options_frame = ttk.LabelFrame(self.encode_frame, text="Options", padding=10)
        options_frame.pack(fill='x', padx=5, pady=5)
        
        # Password option
        ttk.Label(options_frame, text="Password (optional):").grid(row=0, column=0, sticky='w')
        self.password_var = tk.StringVar()
        ttk.Entry(options_frame, textvariable=self.password_var, show='*', width=20).grid(row=0, column=1, padx=5, sticky='w')
        
        # Algorithm selection
        ttk.Label(options_frame, text="Algorithm:").grid(row=1, column=0, sticky='w')
        self.algorithm_var = tk.StringVar(value='lsb')
        algorithm_combo = ttk.Combobox(options_frame, textvariable=self.algorithm_var, 
                                     values=self.engine.get_available_algorithms(), 
                                     state='readonly', width=18)
        algorithm_combo.grid(row=1, column=1, padx=5, sticky='w')
        
        # Action buttons
        button_frame = ttk.Frame(self.encode_frame)
        button_frame.pack(fill='x', padx=5, pady=10)
        
        ttk.Button(button_frame, text="Hide Message", 
                  command=self.encode_message, style="Action.TButton").pack(side='left')
        
        ttk.Button(button_frame, text="Preview", 
                  command=self.preview_encoding).pack(side='left', padx=(10, 0))
        
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_encode_form).pack(side='right')
    
    def create_decode_widgets(self):
        """Create widgets for decoding tab."""
        # Image selection frame
        decode_image_frame = ttk.LabelFrame(self.decode_frame, text="Select Image with Hidden Message", padding=10)
        decode_image_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(decode_image_frame, text="Browse Image", 
                  command=self.load_decode_image).pack(side='left')
        
        self.decode_image_path_var = tk.StringVar()
        ttk.Label(decode_image_frame, textvariable=self.decode_image_path_var).pack(side='left', padx=(10, 0))
        
        # Decode options frame
        decode_options_frame = ttk.LabelFrame(self.decode_frame, text="Decode Options", padding=10)
        decode_options_frame.pack(fill='x', padx=5, pady=5)
        
        # Password option
        ttk.Label(decode_options_frame, text="Password (if used):").grid(row=0, column=0, sticky='w')
        self.decode_password_var = tk.StringVar()
        ttk.Entry(decode_options_frame, textvariable=self.decode_password_var, show='*', width=20).grid(row=0, column=1, padx=5, sticky='w')
        
        # Algorithm selection
        ttk.Label(decode_options_frame, text="Algorithm:").grid(row=1, column=0, sticky='w')
        self.decode_algorithm_var = tk.StringVar(value='lsb')
        decode_algorithm_combo = ttk.Combobox(decode_options_frame, textvariable=self.decode_algorithm_var, 
                                            values=self.engine.get_available_algorithms(), 
                                            state='readonly', width=18)
        decode_algorithm_combo.grid(row=1, column=1, padx=5, sticky='w')
        
        # Action buttons
        decode_button_frame = ttk.Frame(self.decode_frame)
        decode_button_frame.pack(fill='x', padx=5, pady=10)
        
        ttk.Button(decode_button_frame, text="Extract Message", 
                  command=self.decode_message, style="Action.TButton").pack(side='left')
        
        ttk.Button(decode_button_frame, text="Clear", 
                  command=self.clear_decode_form).pack(side='right')
        
        # Results frame
        results_frame = ttk.LabelFrame(self.decode_frame, text="Extracted Message", padding=10)
        results_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.result_text = scrolledtext.ScrolledText(results_frame, height=10, wrap='word', state='disabled')
        self.result_text.pack(fill='both', expand=True)
        
        # Copy button
        ttk.Button(results_frame, text="Copy to Clipboard", 
                  command=self.copy_result).pack(pady=(5, 0))
    
    def load_image(self):
        """Load image for encoding."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff;*.tif"),
                ("All supported", "*.png;*.bmp;*.tiff;*.tif")
            ]
        )
        
        if file_path:
            try:
                if not ImageHandler.is_supported_format(file_path):
                    messagebox.showerror("Error", "Unsupported file format. Please use PNG, BMP, or TIFF.")
                    return
                
                self.current_image, self.current_image_metadata = ImageHandler.load_image(file_path)
                self.image_path_var.set(os.path.basename(file_path))
                self.status_var.set(f"Loaded image: {file_path}")
                
                # Update max message length info
                info = ImageHandler.get_image_info(self.current_image)
                max_chars = info['max_message_length'] - 20  # Reserve space for delimiter
                self.status_var.set(f"Image loaded. Max message length: ~{max_chars} characters")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def load_decode_image(self):
        """Load image for decoding."""
        file_path = filedialog.askopenfilename(
            title="Select Image with Hidden Message",
            filetypes=[
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff;*.tif"),
                ("All supported", "*.png;*.bmp;*.tiff;*.tif")
            ]
        )
        
        if file_path:
            try:
                if not ImageHandler.is_supported_format(file_path):
                    messagebox.showerror("Error", "Unsupported file format.")
                    return
                
                self.decode_image, self.decode_image_metadata = ImageHandler.load_image(file_path)
                self.decode_image_path_var.set(os.path.basename(file_path))
                self.status_var.set(f"Loaded image for decoding: {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def encode_message(self):
        """Encode message into image."""
        if self.current_image is None:
            messagebox.showerror("Error", "Please select an image first.")
            return
        
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Please enter a message to hide.")
            return
        
        # Show progress
        self.status_var.set("Encoding message...")
        self.root.update()
        
        def encode_worker():
            try:
                # Set algorithm
                self.engine.set_algorithm(self.algorithm_var.get())
                
                # Check if message fits
                if not self.engine.can_fit_message(self.current_image, message): # pyright: ignore[reportArgumentType]
                    self.root.after(0, lambda: messagebox.showerror("Error", "Message is too long for this image."))
                    return
                
                # Prepare message (with password if provided)
                password = self.password_var.get() if self.password_var.get() else None
                processed_message = TextHandler.prepare_message(message, password)
                
                # Encode message
                if self.current_image is not None:
                    result_image = self.engine.encode_message(self.current_image, processed_message)
                else:
                    raise ValueError("No image loaded")
                
                # Save result
                self.root.after(0, lambda: self.save_encoded_image(result_image))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Encoding failed: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.status_var.set("Ready"))
        
        # Run encoding in separate thread to prevent GUI freezing
        threading.Thread(target=encode_worker, daemon=True).start()
    
    def save_encoded_image(self, encoded_image):
        """Save encoded image."""
        file_path = filedialog.asksaveasfilename(
            title="Save Encoded Image",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff")
            ]
        )
        
        if file_path:
            try:
                ImageHandler.save_image(encoded_image, file_path, self.current_image_metadata)
                messagebox.showinfo("Success", f"Message hidden successfully!\nSaved to: {file_path}")
                self.status_var.set(f"Encoded image saved: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save image: {str(e)}")
    
    def decode_message(self):
        """Decode message from image."""
        if not hasattr(self, 'decode_image') or self.decode_image is None:
            messagebox.showerror("Error", "Please select an image to decode.")
            return
        
        self.status_var.set("Extracting message...")
        self.root.update()
        
        def decode_worker():
            try:
                # Set algorithm
                self.engine.set_algorithm(self.decode_algorithm_var.get())
                
                # Decode message
                decoded_message = self.engine.decode_message(self.decode_image)
                
                # Process decoded message (with password if provided)
                password = self.decode_password_var.get() if self.decode_password_var.get() else None
                final_message = TextHandler.process_decoded_message(decoded_message, password)
                
                # Display result
                self.root.after(0, lambda: self.display_decoded_message(final_message))
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Decoding failed: {str(e)}"))
            finally:
                self.root.after(0, lambda: self.status_var.set("Ready"))
        
        threading.Thread(target=decode_worker, daemon=True).start()
    
    def display_decoded_message(self, message):
        """Display decoded message."""
        self.result_text.config(state='normal')
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", message)
        self.result_text.config(state='disabled')
        
        if message.strip():
            messagebox.showinfo("Success", "Message extracted successfully!")
            self.status_var.set("Message extracted successfully")
        else:
            messagebox.showwarning("Warning", "No message found or incorrect password.")
            self.status_var.set("No message found")
    
    def preview_encoding(self):
        """Preview encoding without saving."""
        if self.current_image is None:
            messagebox.showerror("Error", "Please select an image first.")
            return
        
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Please enter a message to preview.")
            return
        
        info = ImageHandler.get_image_info(self.current_image)
        max_chars = info['max_message_length'] - 20
        
        preview_info = f"""
Image Information:
- Size: {info['width']} x {info['height']} pixels
- Channels: {info['channels']}
- Max message length: ~{max_chars} characters

Message Information:
- Length: {len(message)} characters
- Can fit: {'Yes' if len(message) <= max_chars else 'No'}
- Password protected: {'Yes' if self.password_var.get() else 'No'}
- Algorithm: {self.algorithm_var.get().upper()}
        """
        
        messagebox.showinfo("Encoding Preview", preview_info.strip())
    
    def copy_result(self):
        """Copy decoded message to clipboard."""
        message = self.result_text.get("1.0", tk.END).strip()
        if message:
            self.root.clipboard_clear()
            self.root.clipboard_append(message)
            self.status_var.set("Message copied to clipboard")
        else:
            messagebox.showwarning("Warning", "No message to copy.")
    
    def clear_encode_form(self):
        """Clear encoding form."""
        self.message_text.delete("1.0", tk.END)
        self.password_var.set("")
        self.image_path_var.set("")
        self.current_image = None
        self.current_image_metadata = None
        self.status_var.set("Encoding form cleared")
    
    def clear_decode_form(self):
        """Clear decoding form."""
        self.decode_password_var.set("")
        self.decode_image_path_var.set("")
        self.result_text.config(state='normal')
        self.result_text.delete("1.0", tk.END)
        self.result_text.config(state='disabled')
        if hasattr(self, 'decode_image'):
            delattr(self, 'decode_image')
        if hasattr(self, 'decode_image_metadata'):
            delattr(self, 'decode_image_metadata')
        self.status_var.set("Decoding form cleared")
    
    def save_result(self):
        """Save current result."""
        message = self.result_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "No message to save.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save Decoded Message",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(message)
                messagebox.showinfo("Success", f"Message saved to: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save message: {str(e)}")
    
    def show_image_info(self):
        """Show detailed image information."""
        if self.current_image is None:
            messagebox.showwarning("Warning", "No image loaded.")
            return
        
        info = ImageHandler.get_image_info(self.current_image)
        info_text = f"""
Image Information:
- Dimensions: {info['width']} x {info['height']} pixels
- Channels: {info['channels']}
- Data type: {info['dtype']}
- Size in memory: {info['size_bytes']:,} bytes
- Shape: {info['shape']}
- Estimated max message length: {info['max_message_length']} characters

File Information:
- Original format: {self.current_image_metadata.get('format', 'Unknown') if self.current_image_metadata else 'Unknown'}
- Original mode: {self.current_image_metadata.get('original_mode', 'Unknown') if self.current_image_metadata else 'Unknown'}
- File path: {self.current_image_metadata.get('filename', 'Unknown') if self.current_image_metadata else 'Unknown'}
        """
        
        messagebox.showinfo("Image Information", info_text.strip())
    
    def show_algorithm_settings(self):
        """Show algorithm settings dialog."""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Algorithm Settings")
        settings_window.geometry("400x300")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Available algorithms
        ttk.Label(settings_window, text="Available Algorithms:", font=('Arial', 12, 'bold')).pack(pady=10)
        
        algorithms_info = {
            'lsb': 'Least Significant Bit - Basic steganography method'
        }
        
        for alg_name, alg_desc in algorithms_info.items():
            frame = ttk.Frame(settings_window)
            frame.pack(fill='x', padx=20, pady=5)
            
            ttk.Label(frame, text=f"• {alg_name.upper()}: {alg_desc}").pack(anchor='w')
        
        ttk.Separator(settings_window).pack(fill='x', padx=20, pady=20)
        
        # Future algorithms note
        note_text = """
Note for Developers:
This architecture is designed to be easily extensible. 
To add new algorithms:

1. Create a new class inheriting from SteganographyAlgorithm
2. Implement encode(), decode(), and can_fit_message() methods
3. Register the algorithm with engine.register_algorithm()

Examples of algorithms you can add:
• DCT-based steganography
• Spread spectrum techniques
• Palette-based methods for indexed images
        """
        
        text_widget = tk.Text(settings_window, height=12, wrap='word', state='disabled')
        text_widget.pack(fill='both', expand=True, padx=20, pady=10)
        text_widget.config(state='normal')
        text_widget.insert('1.0', note_text.strip())
        text_widget.config(state='disabled')
        
        ttk.Button(settings_window, text="Close", command=settings_window.destroy).pack(pady=10)
    
    def show_about(self):
        """Show about dialog."""
        about_text = """
Steganography v1.0

A steganography application for hiding and extracting text messages in images.

Features:
• LSB, DCT, DWT steganography algorithms
• Password protection with encryption
• Support for PNG, BMP, TIFF formats
• Clean, user-friendly interface

Developed for educational purposes.
Use responsibly!

License: MIT
        """
        
        messagebox.showinfo("About", about_text.strip())
    
    def show_usage_guide(self):
        """Show usage guide."""
        guide_window = tk.Toplevel(self.root)
        guide_window.title("Usage Guide")
        guide_window.geometry("600x500")
        guide_window.transient(self.root)
        
        guide_text = """
STEGANOGRAPHY TOOL - USAGE GUIDE

HIDING A MESSAGE:
1. Go to the "Hide Message" tab
2. Click "Browse Image" to select a PNG, BMP, or TIFF image
3. Type your secret message in the text area
4. (Optional) Enter a password for extra security
5. Click "Preview" to check if your message fits
6. Click "Hide Message" and choose where to save the result

EXTRACTING A MESSAGE:
1. Go to the "Extract Message" tab
2. Click "Browse Image" to select an image with a hidden message
3. If the message was password-protected, enter the same password
4. Click "Extract Message"
5. The hidden message will appear in the results area
6. Use "Copy to Clipboard" to copy the message

TIPS:
• Use lossless formats (PNG, BMP, TIFF) to avoid message corruption
• Larger images can hide longer messages
• Write down passwords - they cannot be recovered if lost
• The original image and stego-image will look identical to the naked eye

SUPPORTED FORMATS:
• PNG (recommended) - best compression and quality
• BMP - uncompressed, largest file sizes
• TIFF - good compression, professional use

SECURITY NOTES:
• This tool provides basic steganography, not cryptographic security
• For sensitive data, use additional encryption before hiding
• Be aware that advanced analysis tools may detect hidden messages

DEVELOPMENT:
This tool is designed to be extended. Developers can easily add:
• New steganography algorithms
• Additional image formats
• Advanced encryption methods
        """
        
        text_widget = scrolledtext.ScrolledText(guide_window, wrap='word', state='disabled')
        text_widget.pack(fill='both', expand=True, padx=20, pady=20)
        text_widget.config(state='normal')
        text_widget.insert('1.0', guide_text.strip())
        text_widget.config(state='disabled')
        
        ttk.Button(guide_window, text="Close", command=guide_window.destroy).pack(pady=10)

    def update_status(self, message: str) -> None:
        """Update status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()

    def show_error(self, title: str, message: str) -> None:
        """Show error dialog."""
        messagebox.showerror(title, message)

    def show_info(self, title: str, message: str) -> None:
        """Show info dialog."""
        messagebox.showinfo(title, message)

    def show_warning(self, title: str, message: str) -> None:
        """Show warning dialog."""
        messagebox.showwarning(title, message)

    def _load_recent_files(self) -> list:
        """Load recent files from settings."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('recent_files', [])
        except Exception as e:
            # Return empty list if settings file is corrupted
            print(f"Failed to load recent files: {e}")
        return []

    def _save_recent_files(self):
        """Save recent files to settings."""
        try:
            settings = {'recent_files': self.recent_files}
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception:
            pass

    def _add_recent_file(self, file_path: str):
        """Add file to recent files list."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        self._save_recent_files()
        self._update_recent_menu()

    def _update_recent_menu(self):
        """Update recent files menu."""
        # This will be called when menu is created
        pass

    def _load_settings(self) -> dict:
        """Load GUI settings."""
        default_settings = {
            'window_geometry': '800x600',
            'algorithm': 'lsb',
            'auto_save_location': '',
            'show_preview': True,
            'remember_passwords': False
        }

        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults
                    for key, value in default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
        except Exception:
            pass
        return default_settings

    def _save_settings(self):
        """Save GUI settings."""
        try:
            # Update current settings
            self.settings['window_geometry'] = self.root.geometry()
            self.settings['algorithm'] = self.algorithm_var.get()
            self.settings['recent_files'] = self.recent_files

            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def _restore_settings(self):
        """Restore GUI settings."""
        try:
            # Restore window geometry
            if self.settings.get('window_geometry'):
                self.root.geometry(self.settings['window_geometry'])

            # Restore algorithm selection
            if hasattr(self, 'algorithm_var'):
                self.algorithm_var.set(self.settings.get('algorithm', 'lsb'))

        except Exception:
            pass

    def _on_closing(self):
        """Handle window closing."""
        self._save_settings()
        self.root.destroy()
