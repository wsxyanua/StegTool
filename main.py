#!/usr/bin/env python3
"""
Steganography v1.0 - Desktop Edition
Compact and professional steganography tool matching web interface design.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import numpy as np
import os
import sys
import json
import hashlib
import base64
from typing import Optional


class SimpleEncryption:
    """Simple encryption using built-in hashlib (no external dependencies)."""

    @staticmethod
    def encrypt(message: str, password: str) -> str:
        """Simple encryption using XOR with password hash."""
        if not password:
            return message

        # Create key from password
        key = hashlib.sha256(password.encode()).digest()

        # Convert message to bytes
        message_bytes = message.encode('utf-8')

        # XOR encryption
        encrypted_bytes = bytearray()
        for i, byte in enumerate(message_bytes):
            encrypted_bytes.append(byte ^ key[i % len(key)])

        # Encode to base64 for safe storage
        return base64.b64encode(encrypted_bytes).decode('ascii')

    @staticmethod
    def decrypt(encrypted_message: str, password: str) -> str:
        """Simple decryption using XOR with password hash."""
        if not password:
            return encrypted_message

        try:
            # Create key from password
            key = hashlib.sha256(password.encode()).digest()

            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_message.encode('ascii'))

            # XOR decryption
            decrypted_bytes = bytearray()
            for i, byte in enumerate(encrypted_bytes):
                decrypted_bytes.append(byte ^ key[i % len(key)])

            return decrypted_bytes.decode('utf-8')
        except Exception:
            raise ValueError("Invalid password or corrupted data")


class SimpleSteganography:
    """Ultra simple LSB steganography with optional encryption."""

    @staticmethod
    def encode(image_array, message, password: Optional[str] = None):
        """Hide message in image using LSB."""
        # Encrypt message if password provided
        if password:
            message = SimpleEncryption.encrypt(message, password)
            message = "ENCRYPTED:" + message  # Mark as encrypted

        # Convert message to binary
        binary_message = ''.join(format(ord(char), '08b') for char in message)
        binary_message += '1111111111111110'  # End marker
        
        # Check capacity
        height, width, channels = image_array.shape
        max_capacity = height * width * channels
        
        if len(binary_message) > max_capacity:
            raise ValueError(f"Message too long! Max capacity: {max_capacity // 8} characters")
        
        # Create copy of image
        stego_image = image_array.copy()
        
        # Hide message
        bit_index = 0
        for i in range(height):
            for j in range(width):
                for k in range(channels):
                    if bit_index < len(binary_message):
                        # Modify LSB
                        pixel_value = stego_image[i, j, k]
                        pixel_value = (pixel_value & 0xFE) | int(binary_message[bit_index])
                        stego_image[i, j, k] = pixel_value
                        bit_index += 1
                    else:
                        return stego_image
        
        return stego_image
    
    @staticmethod
    def decode(image_array, password: Optional[str] = None):
        """Extract message from image."""
        height, width, channels = image_array.shape
        binary_message = ""

        # Extract LSBs
        for i in range(height):
            for j in range(width):
                for k in range(channels):
                    binary_message += str(image_array[i, j, k] & 1)

                    # Check for end marker
                    if binary_message.endswith('1111111111111110'):
                        # Remove end marker
                        binary_message = binary_message[:-16]

                        # Convert binary to text
                        message = ""
                        for i in range(0, len(binary_message), 8):
                            byte = binary_message[i:i+8]
                            if len(byte) == 8:
                                message += chr(int(byte, 2))

                        # Decrypt if encrypted
                        if message.startswith("ENCRYPTED:"):
                            if not password:
                                raise ValueError("This message is password protected. Please enter the password.")
                            encrypted_message = message[10:]  # Remove "ENCRYPTED:" prefix
                            message = SimpleEncryption.decrypt(encrypted_message, password)

                        return message

        raise ValueError("No hidden message found")





class CompactGUI:
    """Professional steganography tool matching web interface design."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("STEGANOGRAPHY RE-BIRTH")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        self.root.minsize(600, 500)

        # Set modern styling
        self.root.configure(bg='#ffffff')

        self.stego = SimpleSteganography()
        self.current_image_path = None

        # Portable mode - settings in app folder
        app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
        self.settings_file = os.path.join(app_dir, "settings.json")

        # Load settings and recent files
        self.settings = self.load_settings()
        self.recent_files = self.settings.get('recent_files', [])

        self.setup_gui()
        self.setup_menu()
        self.restore_window_state()

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_gui(self):
        """Setup compact GUI matching web interface."""
        # Header
        header_frame = tk.Frame(self.root, bg='#ffffff', height=80)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        header_frame.pack_propagate(False)

        title_label = tk.Label(header_frame, text="STEGANOGRAPHY",
                              font=('Arial', 20, 'bold'), bg='#ffffff', fg='#000000')
        title_label.pack(side=tk.TOP)

        subtitle_label = tk.Label(header_frame, text="RE-BIRTH 1.0",
                                 font=('Arial', 10), bg='#ffffff', fg='#666666')
        subtitle_label.pack(side=tk.TOP)

        # Main content with tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Hide tab
        hide_frame = ttk.Frame(self.notebook)
        self.notebook.add(hide_frame, text="HIDE")
        self.setup_hide_tab(hide_frame)

        # Extract tab
        extract_frame = ttk.Frame(self.notebook)
        self.notebook.add(extract_frame, text="EXTRACT")
        self.setup_extract_tab(extract_frame)

        # Footer
        footer_frame = tk.Frame(self.root, bg='#ffffff', height=40)
        footer_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        footer_frame.pack_propagate(False)

        footer_label = tk.Label(footer_frame, text="© 2024 STEGANOGRAPHY RE-BIRTH - PROFESSIONAL PRIVACY TOOLS",
                               font=('Arial', 8), bg='#ffffff', fg='#999999')
        footer_label.pack(side=tk.BOTTOM)

    def setup_menu(self):
        """Setup professional menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Image...", command=self.browse_image, accelerator="Ctrl+O")
        file_menu.add_separator()

        # Recent files submenu
        self.recent_menu = tk.Menu(file_menu, tearoff=0)
        file_menu.add_cascade(label="Recent Files", menu=self.recent_menu)
        self.update_recent_menu()

        file_menu.add_separator()
        file_menu.add_command(label="Export Settings...", command=self.export_settings)
        file_menu.add_command(label="Import Settings...", command=self.import_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Clear Recent Files", command=self.clear_recent_files)
        tools_menu.add_command(label="About", command=self.show_about)

        # Keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.browse_image())

    def setup_hide_tab(self, parent):
        """Setup hide message tab."""
        # File selection with recent files
        file_frame = ttk.LabelFrame(parent, text="FILE INPUT")
        file_frame.pack(fill=tk.X, padx=10, pady=5)

        file_button_frame = tk.Frame(file_frame)
        file_button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.file_button = tk.Button(file_button_frame, text="SELECT FILE",
                                    command=self.browse_image, bg='#f0f0f0',
                                    font=('Arial', 10, 'bold'), relief=tk.FLAT, bd=2)
        self.file_button.pack(side=tk.LEFT)

        self.file_label = tk.Label(file_button_frame, text="No file selected",
                                  font=('Arial', 9), fg='#666666')
        self.file_label.pack(side=tk.LEFT, padx=(10, 0))

        # Image info and capacity
        self.info_label = tk.Label(file_frame, text="", font=('Arial', 8), fg='#999999')
        self.info_label.pack(padx=10, pady=(0, 10))

        # Message input with character counter
        msg_frame = ttk.LabelFrame(parent, text="SECRET MESSAGE")
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.message_text = scrolledtext.ScrolledText(msg_frame, height=6, wrap=tk.WORD,
                                                     font=('Arial', 10))
        self.message_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        self.message_text.bind('<KeyRelease>', self.update_char_count)

        self.char_count_label = tk.Label(msg_frame, text="0 characters",
                                        font=('Arial', 8), fg='#666666')
        self.char_count_label.pack(anchor=tk.E, padx=10, pady=(0, 10))

        # Password
        pwd_frame = ttk.LabelFrame(parent, text="PASSWORD (OPTIONAL)")
        pwd_frame.pack(fill=tk.X, padx=10, pady=5)

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(pwd_frame, textvariable=self.password_var,
                                      show="*", font=('Arial', 10))
        self.password_entry.pack(fill=tk.X, padx=10, pady=10)

        # Hide button
        self.hide_button = tk.Button(parent, text="HIDE MESSAGE",
                                    command=self.encode_message, bg='#000000', fg='#ffffff',
                                    font=('Arial', 12, 'bold'), relief=tk.FLAT, bd=0,
                                    state=tk.DISABLED, height=2)
        self.hide_button.pack(fill=tk.X, padx=10, pady=10)

    def setup_extract_tab(self, parent):
        """Setup extract message tab."""
        # File selection
        file_frame = ttk.LabelFrame(parent, text="FILE INPUT")
        file_frame.pack(fill=tk.X, padx=10, pady=5)

        file_button_frame = tk.Frame(file_frame)
        file_button_frame.pack(fill=tk.X, padx=10, pady=10)

        self.extract_file_button = tk.Button(file_button_frame, text="SELECT FILE",
                                           command=self.browse_extract_image, bg='#f0f0f0',
                                           font=('Arial', 10, 'bold'), relief=tk.FLAT, bd=2)
        self.extract_file_button.pack(side=tk.LEFT)

        self.extract_file_label = tk.Label(file_button_frame, text="No file selected",
                                         font=('Arial', 9), fg='#666666')
        self.extract_file_label.pack(side=tk.LEFT, padx=(10, 0))

        # Password
        pwd_frame = ttk.LabelFrame(parent, text="PASSWORD (IF PROTECTED)")
        pwd_frame.pack(fill=tk.X, padx=10, pady=5)

        self.extract_password_var = tk.StringVar()
        self.extract_password_entry = tk.Entry(pwd_frame, textvariable=self.extract_password_var,
                                              show="*", font=('Arial', 10))
        self.extract_password_entry.pack(fill=tk.X, padx=10, pady=10)

        # Extract button
        self.extract_button = tk.Button(parent, text="EXTRACT MESSAGE",
                                       command=self.decode_message, bg='#000000', fg='#ffffff',
                                       font=('Arial', 12, 'bold'), relief=tk.FLAT, bd=0,
                                       state=tk.DISABLED, height=2)
        self.extract_button.pack(fill=tk.X, padx=10, pady=10)

        # Result
        result_frame = ttk.LabelFrame(parent, text="EXTRACTED MESSAGE")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.result_text = scrolledtext.ScrolledText(result_frame, height=6, wrap=tk.WORD,
                                                    font=('Arial', 10), state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def browse_image(self): # type: ignore
        """Browse for image file."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff *.tif"),
                ("All supported", "*.png *.bmp *.tiff *.tif")
            ]
        )

        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        """Load image and update UI."""
        try:
            self.current_image_path = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=filename)
            self.hide_button.config(state=tk.NORMAL)

            # Add to recent files
            self.add_recent_file(file_path)

            # Calculate capacity
            img = Image.open(file_path)
            width, height = img.size
            channels = len(img.getbands())
            max_chars = (width * height * channels) // 8 - 2

            self.info_label.config(text=f"Size: {width}x{height}, Capacity: {max_chars:,} chars")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")

    def update_char_count(self, event=None):
        """Update character count."""
        text = self.message_text.get("1.0", tk.END).strip()
        count = len(text)
        self.char_count_label.config(text=f"{count} characters")

    def browse_extract_image(self):
        """Browse for extract image file."""
        file_path = filedialog.askopenfilename(
            title="Select Image with Hidden Message",
            filetypes=[
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff *.tif"),
                ("All supported", "*.png *.bmp *.tiff *.tif")
            ]
        )

        if file_path:
            self.extract_image_path = file_path
            filename = os.path.basename(file_path)
            self.extract_file_label.config(text=filename)
            self.extract_button.config(state=tk.NORMAL)
    
    def setup_encode_tab(self, parent):
        """Setup encode tab."""
        # Image selection with drag & drop
        ttk.Label(parent, text="1. Select Image (or drag & drop):").pack(anchor=tk.W, pady=(10, 5))

        image_frame = ttk.Frame(parent)
        image_frame.pack(fill=tk.X, pady=(0, 10))

        self.image_path_var = tk.StringVar()
        self.image_entry = ttk.Entry(image_frame, textvariable=self.image_path_var, state="readonly")
        self.image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(image_frame, text="Browse", command=self.browse_image).pack(side=tk.RIGHT, padx=(5, 0))

        # Drag & drop area
        self.drop_frame = ttk.LabelFrame(parent, text="Drag & Drop Area")
        self.drop_frame.pack(fill=tk.X, pady=(0, 10))

        self.drop_label = ttk.Label(self.drop_frame, text="📁 Drag image files here\nSupported: PNG, BMP, TIFF, JPG",
                                   justify=tk.CENTER, font=('Arial', 10))
        self.drop_label.pack(pady=20)

        # Image preview
        self.preview_frame = ttk.LabelFrame(parent, text="Image Preview")
        self.preview_frame.pack(fill=tk.X, pady=(0, 10))

        self.preview_label = ttk.Label(self.preview_frame, text="No image selected")
        self.preview_label.pack(pady=10)

        # Capacity info
        self.capacity_label = ttk.Label(parent, text="Capacity: Select an image to see max message size")
        self.capacity_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Message input
        ttk.Label(parent, text="2. Enter Secret Message:").pack(anchor=tk.W, pady=(10, 5))

        self.message_text = scrolledtext.ScrolledText(parent, height=6, wrap=tk.WORD)
        self.message_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Password section
        password_frame = ttk.LabelFrame(parent, text="Password Protection (Optional)")
        password_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(password_frame, text="Password:").pack(anchor=tk.W, padx=10, pady=(5, 0))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(password_frame, textvariable=self.password_var, show="*")
        self.password_entry.pack(fill=tk.X, padx=10, pady=(0, 5))



        # Encode button
        ttk.Button(parent, text="Hide Message", command=self.encode_message).pack(pady=10)
        
        # Status
        self.encode_status = ttk.Label(parent, text="Ready")
        self.encode_status.pack(pady=(0, 10))
    
    def setup_decode_tab(self, parent):
        """Setup decode tab."""
        # Image selection
        ttk.Label(parent, text="1. Select Image with Hidden Message:").pack(anchor=tk.W, pady=(10, 5))
        
        decode_image_frame = ttk.Frame(parent)
        decode_image_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.decode_image_path_var = tk.StringVar()
        ttk.Entry(decode_image_frame, textvariable=self.decode_image_path_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(decode_image_frame, text="Browse", command=self.browse_decode_image).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Password section for decode
        decode_password_frame = ttk.LabelFrame(parent, text="Password (if message is protected)")
        decode_password_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(decode_password_frame, text="Password:").pack(anchor=tk.W, padx=10, pady=(5, 0))
        self.decode_password_var = tk.StringVar()
        self.decode_password_entry = ttk.Entry(decode_password_frame, textvariable=self.decode_password_var, show="*")
        self.decode_password_entry.pack(fill=tk.X, padx=10, pady=(0, 5))



        # Decode button
        ttk.Button(parent, text="Extract Message", command=self.decode_message).pack(pady=10)

        # Result
        ttk.Label(parent, text="Extracted Message:").pack(anchor=tk.W, pady=(10, 5))
        
        self.result_text = scrolledtext.ScrolledText(parent, height=10, wrap=tk.WORD, state="disabled")
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Status
        self.decode_status = ttk.Label(parent, text="Ready")
        self.decode_status.pack(pady=(0, 10))
    
    def browse_image(self):
        """Browse for image file."""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("All supported", "*.png *.bmp *.tiff *.tif *.jpg *.jpeg"),
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff *.tif"),
                ("JPEG files", "*.jpg *.jpeg")
            ]
        )

        if file_path:
            self.load_image(file_path)
    
    def browse_decode_image(self):
        """Browse for decode image file."""
        file_path = filedialog.askopenfilename(
            title="Select Image with Hidden Message",
            filetypes=[
                ("PNG files", "*.png"),
                ("BMP files", "*.bmp"),
                ("TIFF files", "*.tiff *.tif"),
                ("All supported", "*.png *.bmp *.tiff *.tif")
            ]
        )
        
        if file_path:
            self.decode_image_path_var.set(file_path)
    
    def encode_message(self):
        """Encode message into image."""
        try:
            # Validate inputs
            if not self.current_image_path:
                messagebox.showerror("Error", "Please select an image first")
                return

            message = self.message_text.get("1.0", tk.END).strip()
            if not message:
                messagebox.showerror("Error", "Please enter a message")
                return

            # Load image
            image = Image.open(self.current_image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')

            image_array = np.array(image)

            # Get password
            password = self.password_var.get().strip() or None

            # Encode message
            stego_array = self.stego.encode(image_array, message, password)

            # Save result
            output_path = filedialog.asksaveasfilename(
                title="Save Hidden Message Image",
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("BMP files", "*.bmp"),
                    ("TIFF files", "*.tiff")
                ]
            )

            if output_path:
                stego_image = Image.fromarray(stego_array)
                stego_image.save(output_path)
                messagebox.showinfo("Success", f"Message hidden successfully!\nSaved: {os.path.basename(output_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to hide message:\n{str(e)}")
    
    def decode_message(self):
        """Decode message from image."""
        try:
            # Validate input
            if not hasattr(self, 'extract_image_path') or not self.extract_image_path:
                messagebox.showerror("Error", "Please select an image first")
                return

            # Load image
            image = Image.open(self.extract_image_path)
            if image.mode != 'RGB':
                image = image.convert('RGB')

            image_array = np.array(image)

            # Get password
            password = self.extract_password_var.get().strip() or None

            # Decode message
            message = self.stego.decode(image_array, password)

            # Display result
            self.result_text.config(state="normal")
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert("1.0", message)
            self.result_text.config(state="disabled")

            messagebox.showinfo("Success", "Message extracted successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract message:\n{str(e)}")

    def add_recent_file(self, file_path):
        """Add file to recent files."""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)

        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:10]  # Keep only 10 recent files
        self.save_settings()
        self.update_recent_menu()

    def update_recent_menu(self):
        """Update recent files menu."""
        self.recent_menu.delete(0, tk.END)

        if not self.recent_files:
            self.recent_menu.add_command(label="No recent files", state="disabled")
        else:
            for file_path in self.recent_files[:10]:
                if os.path.exists(file_path):
                    filename = os.path.basename(file_path)
                    self.recent_menu.add_command(label=filename,
                                               command=lambda f=file_path: self.load_image(f))

    def clear_recent_files(self):
        """Clear recent files list."""
        self.recent_files.clear()
        self.save_settings()
        self.update_recent_menu()

    def load_settings(self):
        """Load settings from file."""
        default_settings = {
            'recent_files': [],
            'window_geometry': '700x600',
            'window_state': 'normal'
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

    def save_settings(self):
        """Save settings to file."""
        try:
            self.settings['window_geometry'] = self.root.geometry()
            self.settings['window_state'] = self.root.state()
            self.settings['recent_files'] = self.recent_files

            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception:
            pass

    def restore_window_state(self):
        """Restore window state."""
        try:
            if self.settings.get('window_geometry'):
                self.root.geometry(self.settings['window_geometry'])
        except Exception:
            pass

    def export_settings(self):
        """Export settings to file."""
        try:
            file_path = filedialog.asksaveasfilename(
                title="Export Settings",
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if file_path:
                with open(file_path, 'w') as f:
                    json.dump(self.settings, f, indent=2)
                messagebox.showinfo("Success", f"Settings exported to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to export settings: {str(e)}")

    def import_settings(self):
        """Import settings from file."""
        try:
            file_path = filedialog.askopenfilename(
                title="Import Settings",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )

            if file_path:
                with open(file_path, 'r') as f:
                    imported_settings = json.load(f)

                # Merge settings
                self.settings.update(imported_settings)
                self.recent_files = self.settings.get('recent_files', [])

                self.update_recent_menu()
                self.save_settings()

                messagebox.showinfo("Success", "Settings imported successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to import settings: {str(e)}")

    def show_about(self):
        """Show about dialog."""
        about_text = """STEGANOGRAPHY RE-BIRTH v1.0

Professional steganography tool for hiding messages in images.

Features:
• LSB Steganography with password protection
• Support for PNG, BMP, TIFF formats
• Recent files management
• Settings export/import
• Portable mode

Built with Python & tkinter
No external dependencies required

© 2024 - STEGANOGRAPHY RE-BIRTH"""

        messagebox.showinfo("About", about_text)

    def on_closing(self):
        """Handle window closing."""
        self.save_settings()
        self.root.destroy()

    def run(self):
        """Run the GUI."""
        self.root.mainloop()


def main():
    """Main function."""
    try:
        app = CompactGUI()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()

