"""
Custom dialog windows for the steganography GUI application. 

This module provides specialized dialog windows including:
- Password input dialogs
- Progress dialogs
- Settings dialogs
- About dialog
- Error dialogs with details
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable


class PasswordDialog:
    """Custom password input dialog with confirmation."""

    def __init__(self, parent: tk.Tk, title: str = "Password Required",
                 message: str = "Enter password:", confirm: bool = False):
        self.parent = parent
        self.title = title
        self.message = message
        self.confirm = confirm
        self.result: Optional[str] = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

        self._create_widgets()

    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Message label
        ttk.Label(main_frame, text=self.message, font=('Arial', 10)).pack(pady=(0, 10))

        # Password entry
        ttk.Label(main_frame, text="Password:").pack(anchor='w')
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var,
                                       show='*', width=40)
        self.password_entry.pack(fill='x', pady=(5, 10))

        # Confirm password entry (if needed)
        if self.confirm:
            ttk.Label(main_frame, text="Confirm Password:").pack(anchor='w')
            self.confirm_var = tk.StringVar()
            self.confirm_entry = ttk.Entry(main_frame, textvariable=self.confirm_var,
                                          show='*', width=40)
            self.confirm_entry.pack(fill='x', pady=(5, 10))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(10, 0))

        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="OK", command=self._ok).pack(side='right')

        # Bind Enter key
        self.dialog.bind('<Return>', lambda _: self._ok())
        self.dialog.bind('<Escape>', lambda _: self._cancel())

        # Focus on password entry
        self.password_entry.focus()

    def _ok(self):
        """Handle OK button."""
        password = self.password_var.get()

        if not password:
            messagebox.showerror("Error", "Password cannot be empty", parent=self.dialog)
            return

        if self.confirm:
            confirm_password = self.confirm_var.get()
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match", parent=self.dialog)
                return

        self.result = password
        self.dialog.destroy()

    def _cancel(self):
        """Handle Cancel button."""
        self.result = None
        self.dialog.destroy()

    def show(self) -> Optional[str]:
        """Show dialog and return password."""
        self.dialog.wait_window()
        return self.result


class ProgressDialog:
    """Progress dialog with cancel support."""

    def __init__(self, parent: tk.Tk, title: str = "Processing",
                 message: str = "Please wait...", cancelable: bool = True):
        self.parent = parent
        self.title = title
        self.message = message
        self.cancelable = cancelable
        self.cancelled = False
        self.cancel_callback: Optional[Callable] = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

        # Prevent closing
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_widgets()

    def _create_widgets(self):
        """Create progress dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Message label
        self.message_label = ttk.Label(main_frame, text=self.message, font=('Arial', 10))
        self.message_label.pack(pady=(0, 15))

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=300)
        self.progress.pack(pady=(0, 15))
        self.progress.start(10)

        # Cancel button
        if self.cancelable:
            self.cancel_button = ttk.Button(main_frame, text="Cancel", command=self._cancel)
            self.cancel_button.pack()

    def _cancel(self):
        """Handle cancel button."""
        self.cancelled = True
        if self.cancel_callback:
            self.cancel_callback()
        self.close()

    def _on_close(self):
        """Handle window close."""
        if self.cancelable:
            self._cancel()

    def update_message(self, message: str):
        """Update progress message."""
        self.message_label.config(text=message)
        self.dialog.update()

    def set_cancel_callback(self, callback: Callable):
        """Set callback for cancel operation."""
        self.cancel_callback = callback

    def close(self):
        """Close the dialog."""
        self.progress.stop()
        self.dialog.destroy()


class SettingsDialog:
    """Settings configuration dialog."""

    def __init__(self, parent: tk.Tk, current_settings: dict):
        self.parent = parent
        self.current_settings = current_settings.copy()
        self.result: Optional[dict] = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

        self._create_widgets()

    def _create_widgets(self):
        """Create settings widgets."""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill='both', expand=True)

        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill='both', expand=True, pady=(0, 10))

        # General tab
        general_frame = ttk.Frame(notebook, padding="10")
        notebook.add(general_frame, text="General")

        # Default algorithm
        ttk.Label(general_frame, text="Default Algorithm:").pack(anchor='w')
        self.algorithm_var = tk.StringVar(value=self.current_settings.get('default_algorithm', 'lsb'))
        algorithm_combo = ttk.Combobox(general_frame, textvariable=self.algorithm_var,
                                      values=['lsb', 'dct', 'adaptive_lsb'], state='readonly')
        algorithm_combo.pack(fill='x', pady=(5, 15))

        # Auto-save results
        self.autosave_var = tk.BooleanVar(value=self.current_settings.get('auto_save', True))
        ttk.Checkbutton(general_frame, text="Auto-save results",
                       variable=self.autosave_var).pack(anchor='w', pady=(0, 10))

        # Show warnings
        self.warnings_var = tk.BooleanVar(value=self.current_settings.get('show_warnings', True))
        ttk.Checkbutton(general_frame, text="Show security warnings",
                       variable=self.warnings_var).pack(anchor='w', pady=(0, 10))

        # Security tab
        security_frame = ttk.Frame(notebook, padding="10")
        notebook.add(security_frame, text="Security")

        # Password strength
        ttk.Label(security_frame, text="Minimum Password Length:").pack(anchor='w')
        self.min_password_var = tk.StringVar(value=str(self.current_settings.get('min_password_length', 8)))
        password_spin = ttk.Spinbox(security_frame, from_=4, to=32, textvariable=self.min_password_var)
        password_spin.pack(fill='x', pady=(5, 15))

        # Require encryption
        self.require_encryption_var = tk.BooleanVar(value=self.current_settings.get('require_encryption', False))
        ttk.Checkbutton(security_frame, text="Always require password encryption",
                       variable=self.require_encryption_var).pack(anchor='w', pady=(0, 10))

        # Clear clipboard
        self.clear_clipboard_var = tk.BooleanVar(value=self.current_settings.get('clear_clipboard', True))
        ttk.Checkbutton(security_frame, text="Clear clipboard after operations",
                       variable=self.clear_clipboard_var).pack(anchor='w', pady=(0, 10))

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x')

        ttk.Button(button_frame, text="Cancel", command=self._cancel).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Apply", command=self._apply).pack(side='right')
        ttk.Button(button_frame, text="Reset to Defaults", command=self._reset).pack(side='left')

    def _apply(self):
        """Apply settings."""
        self.result = {
            'default_algorithm': self.algorithm_var.get(),
            'auto_save': self.autosave_var.get(),
            'show_warnings': self.warnings_var.get(),
            'min_password_length': int(self.min_password_var.get()),
            'require_encryption': self.require_encryption_var.get(),
            'clear_clipboard': self.clear_clipboard_var.get()
        }
        self.dialog.destroy()

    def _cancel(self):
        """Cancel settings."""
        self.result = None
        self.dialog.destroy()

    def _reset(self):
        """Reset to default settings."""
        self.algorithm_var.set('lsb')
        self.autosave_var.set(True)
        self.warnings_var.set(True)
        self.min_password_var.set('8')
        self.require_encryption_var.set(False)
        self.clear_clipboard_var.set(True)

    def show(self) -> Optional[dict]:
        """Show dialog and return settings."""
        self.dialog.wait_window()
        return self.result


class AboutDialog:
    """About dialog with application information."""

    def __init__(self, parent: tk.Tk):
        self.parent = parent

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("About")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Center dialog
        self.dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

        self._create_widgets()

    def _create_widgets(self):
        """Create about dialog widgets."""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)

        # Title
        title_label = ttk.Label(main_frame, text="Open Source Steganography Tool",
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 5))

        # Version
        version_label = ttk.Label(main_frame, text="Version 1.0.0",
                                 font=('Arial', 12))
        version_label.pack(pady=(0, 15))

        # Description
        desc_text = """A simple steganography tool for hiding messages in images.

Features:
• LSB, DCT, DWT steganography algorithms
• Password protection with encryption
• Support for PNG, BMP, TIFF formats
• Clean, user-friendly interface

Use responsibly!"""

        desc_label = ttk.Label(main_frame, text=desc_text, justify='left',
                              font=('Arial', 9))
        desc_label.pack(pady=(0, 15))

        # Links frame
        links_frame = ttk.Frame(main_frame)
        links_frame.pack(fill='x', pady=(0, 15))

        # GitHub link (placeholder)
        github_label = ttk.Label(links_frame, text="GitHub: github.com/hugle2012/steganography-letrongvang",
                                font=('Arial', 9), foreground='blue')
        github_label.pack(anchor='w')

        # License
        license_label = ttk.Label(links_frame, text="License: MIT License",
                                 font=('Arial', 9))
        license_label.pack(anchor='w')

        # Author
        author_label = ttk.Label(links_frame, text="Author: hugle2012",
                                font=('Arial', 9))
        author_label.pack(anchor='w')

        # Close button
        ttk.Button(main_frame, text="Close", command=self.dialog.destroy).pack(pady=(10, 0))


def show_error_dialog(parent: tk.Tk, title: str, message: str, details: str = None): # type: ignore
    """Show error dialog with optional details."""
    if details:
        # Create custom error dialog with details
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("500x300")
        dialog.transient(parent)
        dialog.grab_set()

        # Center dialog
        dialog.geometry("+%d+%d" % (
            parent.winfo_rootx() + 50,
            parent.winfo_rooty() + 50
        ))

        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill='both', expand=True)

        # Error message
        ttk.Label(main_frame, text=message, font=('Arial', 10, 'bold'),
                 foreground='red').pack(anchor='w', pady=(0, 10))

        # Details
        ttk.Label(main_frame, text="Details:", font=('Arial', 9, 'bold')).pack(anchor='w')

        details_text = tk.Text(main_frame, height=10, wrap='word', font=('Courier', 8))
        details_text.pack(fill='both', expand=True, pady=(5, 10))
        details_text.insert('1.0', details)
        details_text.config(state='disabled')

        # Scrollbar for details
        scrollbar = ttk.Scrollbar(details_text)
        scrollbar.pack(side='right', fill='y')
        details_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=details_text.yview)

        # Close button
        ttk.Button(main_frame, text="Close", command=dialog.destroy).pack(pady=(5, 0))

    else:
        # Use standard error dialog
        messagebox.showerror(title, message, parent=parent)


def show_info_dialog(parent: tk.Tk, title: str, message: str):
    """Show information dialog."""
    messagebox.showinfo(title, message, parent=parent)


def show_warning_dialog(parent: tk.Tk, title: str, message: str) -> bool:
    """Show warning dialog with Yes/No options."""
    return messagebox.askyesno(title, message, parent=parent)


def ask_save_file(parent: tk.Tk, title: str = "Save File",
                  filetypes: Optional[list] = None, defaultextension: str = ".txt") -> Optional[str]:
    """Ask user to select save file location."""
    from tkinter import filedialog

    if filetypes is None:
        filetypes = [("All files", "*.*")]

    return filedialog.asksaveasfilename(
        parent=parent,
        title=title,
        filetypes=filetypes,
        defaultextension=defaultextension
    )


def ask_open_file(parent: tk.Tk, title: str = "Open File",
                  filetypes: list = None) -> Optional[str]: # pyright: ignore[reportArgumentType]
    """Ask user to select file to open."""
    from tkinter import filedialog

    if filetypes is None:
        filetypes = [("All files", "*.*")]

    return filedialog.askopenfilename(
        parent=parent,
        title=title,
        filetypes=filetypes
    )


def ask_directory(parent: tk.Tk, title: str = "Select Directory") -> Optional[str]:
    """Ask user to select directory."""
    from tkinter import filedialog

    return filedialog.askdirectory(
        parent=parent,
        title=title
    )