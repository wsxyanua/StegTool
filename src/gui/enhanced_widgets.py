"""
Enhanced GUI widgets for modern steganography interface. 

This module provides advanced GUI components including:
- Drag & drop file handling
- Image preview with zoom
- Progress bars with animations
- Modern styled widgets
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from typing import Optional, Callable
import os


class DragDropFrame(tk.Frame):
    """Frame with drag and drop file support."""
    
    def __init__(self, parent, on_drop_callback: Optional[Callable] = None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_drop_callback = on_drop_callback
        
        # Configure drag and drop
        self.configure(relief='ridge', bd=2, bg='#f0f0f0')
        
        # Create drop label
        self.drop_label = tk.Label(
            self,
            text="Drag & Drop files here\nor click to browse",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#666666'
        )
        self.drop_label.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Bind events
        self.bind('<Button-1>', self._on_click)
        self.drop_label.bind('<Button-1>', self._on_click)
        
        # Try to enable drag and drop (Windows specific)
        try:
            self._setup_drag_drop()
        except Exception as e:
            # Fallback to click-only mode if drag-drop setup fails
            print(f"Drag-drop setup failed: {e}")
    
    def _setup_drag_drop(self):
        """Setup drag and drop functionality (Windows)."""
        try:
            import tkinterdnd2 as tkdnd  # type: ignore

            # Make this a drop target
            self.drop_target_register(tkdnd.DND_FILES)  # type: ignore
            self.dnd_bind('<<Drop>>', self._on_drop)  # type: ignore
            self.dnd_bind('<<DragEnter>>', self._on_drag_enter)  # type: ignore
            self.dnd_bind('<<DragLeave>>', self._on_drag_leave)  # type: ignore

        except (ImportError, AttributeError):
            # tkinterdnd2 not available or methods not found, use click only
            pass
    
    def _on_click(self, event=None):  # noqa: ARG002
        """Handle click to browse files."""
        file_path = filedialog.askopenfilename(
            title="Select file",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif"),
                ("Audio files", "*.wav *.flac *.aiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path and self.on_drop_callback:
            self.on_drop_callback([file_path])
    
    def _on_drop(self, event):
        """Handle file drop."""
        files = self.tk.splitlist(event.data)
        if files and self.on_drop_callback:
            self.on_drop_callback(files)
    
    def _on_drag_enter(self, event):  # noqa: ARG002
        """Handle drag enter."""
        self.configure(bg='#e0e0e0')
        self.drop_label.configure(bg='#e0e0e0', fg='#333333')

    def _on_drag_leave(self, event):  # noqa: ARG002
        """Handle drag leave."""
        self.configure(bg='#f0f0f0')
        self.drop_label.configure(bg='#f0f0f0', fg='#666666')
    
    def set_status(self, text: str, color: str = '#666666'):
        """Update drop zone status text."""
        self.drop_label.configure(text=text, fg=color)


class ImagePreviewWidget(tk.Frame):
    """Widget for displaying image previews with zoom controls."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.current_image = None
        self.current_photo = None
        self.zoom_factor = 1.0
        self.max_size = (400, 300)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create preview widgets."""
        # Control frame
        control_frame = tk.Frame(self)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        tk.Label(control_frame, text="Image Preview:", font=('Arial', 10, 'bold')).pack(side='left')
        
        # Zoom controls
        zoom_frame = tk.Frame(control_frame)
        zoom_frame.pack(side='right')
        
        tk.Button(zoom_frame, text="Zoom In", command=self._zoom_in, width=8).pack(side='left', padx=2)
        tk.Button(zoom_frame, text="Zoom Out", command=self._zoom_out, width=8).pack(side='left', padx=2)
        tk.Button(zoom_frame, text="Fit", command=self._zoom_fit, width=8).pack(side='left', padx=2)
        
        # Image canvas with scrollbars
        canvas_frame = tk.Frame(self, relief='sunken', bd=2)
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.canvas = tk.Canvas(canvas_frame, bg='white')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_frame, orient='vertical', command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_frame, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Info label
        self.info_label = tk.Label(self, text="No image loaded", font=('Arial', 9), fg='#666666')
        self.info_label.pack(fill='x', padx=5, pady=2)
    
    def load_image(self, image_path: str):
        """Load and display image."""
        try:
            self.current_image = Image.open(image_path)
            self.zoom_factor = 1.0
            self._update_display()
            
            # Update info
            width, height = self.current_image.size
            file_size = os.path.getsize(image_path) / 1024  # KB
            self.info_label.configure(
                text=f"Size: {width}x{height} | File: {file_size:.1f} KB | Zoom: {self.zoom_factor:.1f}x"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def _update_display(self):
        """Update image display with current zoom."""
        if not self.current_image:
            return
        
        # Calculate display size
        width, height = self.current_image.size
        display_width = int(width * self.zoom_factor)
        display_height = int(height * self.zoom_factor)
        
        # Resize image for display
        if self.zoom_factor != 1.0:
            display_image = self.current_image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        else:
            display_image = self.current_image
        
        # Convert to PhotoImage
        self.current_photo = ImageTk.PhotoImage(display_image)
        
        # Clear canvas and add image
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor='nw', image=self.current_photo)
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Update info
        self.info_label.configure(
            text=f"Size: {width}x{height} | Display: {display_width}x{display_height} | Zoom: {self.zoom_factor:.1f}x"
        )
    
    def _zoom_in(self):
        """Zoom in."""
        if self.current_image and self.zoom_factor < 5.0:
            self.zoom_factor *= 1.2
            self._update_display()
    
    def _zoom_out(self):
        """Zoom out."""
        if self.current_image and self.zoom_factor > 0.1:
            self.zoom_factor /= 1.2
            self._update_display()
    
    def _zoom_fit(self):
        """Fit image to canvas."""
        if not self.current_image:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            return
        
        image_width, image_height = self.current_image.size
        
        # Calculate zoom to fit
        zoom_x = canvas_width / image_width
        zoom_y = canvas_height / image_height
        self.zoom_factor = min(zoom_x, zoom_y, 1.0)  # Don't zoom in beyond 100%
        
        self._update_display()
    
    def clear(self):
        """Clear the preview."""
        self.current_image = None
        self.current_photo = None
        self.canvas.delete("all")
        self.info_label.configure(text="No image loaded")


class AnimatedProgressBar(tk.Frame):
    """Animated progress bar with status text."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.is_running = False
        self.animation_thread = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create progress widgets."""
        # Status label
        self.status_label = tk.Label(self, text="Ready", font=('Arial', 9))
        self.status_label.pack(fill='x', pady=(0, 5))
        
        # Progress bar
        self.progress = ttk.Progressbar(self, mode='determinate', length=300)
        self.progress.pack(fill='x', pady=(0, 5))
        
        # Percentage label
        self.percent_label = tk.Label(self, text="0%", font=('Arial', 8), fg='#666666')
        self.percent_label.pack()
    
    def start(self, status_text: str = "Processing..."):
        """Start animated progress."""
        self.is_running = True
        self.status_label.configure(text=status_text)
        self.progress.configure(mode='indeterminate')
        self.progress.start(10)
        self.percent_label.configure(text="Working...")
    
    def update_progress(self, value: float, status_text: Optional[str] = None):
        """Update progress value (0-100)."""
        if not self.is_running:
            self.is_running = True
            self.progress.configure(mode='determinate')
            self.progress.stop()
        
        self.progress['value'] = value
        self.percent_label.configure(text=f"{value:.1f}%")
        
        if status_text:
            self.status_label.configure(text=status_text)
    
    def finish(self, status_text: str = "Completed"):
        """Finish progress."""
        self.is_running = False
        self.progress.stop()
        self.progress.configure(mode='determinate')
        self.progress['value'] = 100
        self.status_label.configure(text=status_text)
        self.percent_label.configure(text="100%")
    
    def reset(self):
        """Reset progress bar."""
        self.is_running = False
        self.progress.stop()
        self.progress.configure(mode='determinate')
        self.progress['value'] = 0
        self.status_label.configure(text="Ready")
        self.percent_label.configure(text="0%")


class ModernButton(tk.Button):
    """Modern styled button with hover effects."""
    
    def __init__(self, parent, **kwargs):
        # Default styling
        default_style = {
            'font': ('Arial', 10),
            'relief': 'flat',
            'bd': 0,
            'padx': 20,
            'pady': 8,
            'bg': '#007acc',
            'fg': 'white',
            'activebackground': '#005a9e',
            'activeforeground': 'white',
            'cursor': 'hand2'
        }
        
        # Merge with provided kwargs
        default_style.update(kwargs)
        
        super().__init__(parent, **default_style)
        
        # Store original colors
        self.normal_bg = default_style['bg']
        self.hover_bg = '#005a9e'
        
        # Bind hover events
        self.bind('<Enter>', self._on_enter)
        self.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event):  # noqa: ARG002
        """Handle mouse enter."""
        self.configure(bg=self.hover_bg)

    def _on_leave(self, event):  # noqa: ARG002
        """Handle mouse leave."""
        self.configure(bg=self.normal_bg)


class StatusBar(tk.Frame):
    """Status bar with multiple sections."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, relief='sunken', bd=1, **kwargs)
        
        # Main status label
        self.status_label = tk.Label(self, text="Ready", anchor='w', font=('Arial', 9))
        self.status_label.pack(side='left', fill='x', expand=True, padx=5)
        
        # Additional info labels
        self.info_labels = []
        
        # Separator
        separator = tk.Frame(self, width=1, bg='#cccccc')
        separator.pack(side='right', fill='y', padx=2)
        
        # Time label
        self.time_label = tk.Label(self, text="", anchor='e', font=('Arial', 8), fg='#666666')
        self.time_label.pack(side='right', padx=5)
    
    def set_status(self, text: str):
        """Set main status text."""
        self.status_label.configure(text=text)
    
    def set_time(self, text: str):
        """Set time text."""
        self.time_label.configure(text=text)
    
    def add_info_section(self, text: str = "") -> tk.Label:
        """Add an info section and return the label."""
        # Separator
        separator = tk.Frame(self, width=1, bg='#cccccc')
        separator.pack(side='right', fill='y', padx=2)
        
        # Info label
        info_label = tk.Label(self, text=text, anchor='e', font=('Arial', 8), fg='#666666')
        info_label.pack(side='right', padx=5)
        
        self.info_labels.append(info_label)
        return info_label


class ToolTip:
    """Simple tooltip widget."""
    
    def __init__(self, widget, text: str):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        self.widget.bind('<Enter>', self._on_enter)
        self.widget.bind('<Leave>', self._on_leave)
    
    def _on_enter(self, event=None):  # noqa: ARG002
        """Show tooltip."""
        if self.tooltip_window:
            return

        x, y, _, _ = self.widget.bbox("insert") if hasattr(self.widget, 'bbox') else (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            self.tooltip_window,
            text=self.text,
            background='#ffffe0',
            relief='solid',
            borderwidth=1,
            font=('Arial', 8)
        )
        label.pack()

    def _on_leave(self, event=None):  # noqa: ARG002
        """Hide tooltip."""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
