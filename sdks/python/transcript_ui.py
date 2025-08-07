"""
Real-time Transcript UI Window for Omi Python SDK
Displays live transcriptions from the Omi device in a native Tkinter window.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import queue
from datetime import datetime
import json
import os

class TranscriptWindow:
    """Real-time transcript display window with advanced features."""
    
    def __init__(self, title="🎧 Omi Live Transcript"):
        self.root = None
        self.text_widget = None
        self.status_label = None
        self.memory_count = 0
        self.transcript_count = 0
        self.ui_queue = queue.Queue()
        self.running = True
        
        # Configuration
        self.config = {
            'font_family': 'Consolas',
            'font_size': 11,
            'bg_color': '#1e1e1e',
            'text_color': '#ffffff',
            'accent_color': '#007acc',
            'memory_color': '#ffaa00',
            'timestamp_color': '#888888'
        }
        
        # Start the UI in a separate thread
        self.ui_thread = threading.Thread(target=self._create_window, args=(title,), daemon=True)
        self.ui_thread.start()
    
    def _create_window(self, title):
        """Create and run the Tkinter window in a separate thread."""
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry("800x600")
        self.root.configure(bg=self.config['bg_color'])
        
        # Configure style for dark theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background=self.config['bg_color'])
        style.configure('Dark.TLabel', background=self.config['bg_color'], foreground=self.config['text_color'])
        
        # Create the main frame
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Status bar at the top
        self._create_status_bar(main_frame)
        
        # Main transcript area
        self._create_transcript_area(main_frame)
        
        # Control buttons at the bottom
        self._create_control_buttons(main_frame)
        
        # Start the periodic update checker
        self.root.after(100, self._check_queue)
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Start the main loop
        self.root.mainloop()
    
    def _create_status_bar(self, parent):
        """Create the status bar showing connection and memory info."""
        status_frame = ttk.Frame(parent, style='Dark.TFrame')
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(
            status_frame, 
            text="🔄 Initializing...", 
            style='Dark.TLabel',
            font=(self.config['font_family'], 10)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Memory counter
        self.memory_label = ttk.Label(
            status_frame,
            text="💾 Memories: 0",
            style='Dark.TLabel', 
            font=(self.config['font_family'], 10)
        )
        self.memory_label.pack(side=tk.RIGHT)
    
    def _create_transcript_area(self, parent):
        """Create the main scrollable transcript text area."""
        # Frame for the text widget
        text_frame = ttk.Frame(parent, style='Dark.TFrame')
        text_frame.pack(expand=True, fill=tk.BOTH, pady=(0, 10))
        
        # ScrolledText widget for auto-scrolling
        self.text_widget = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=(self.config['font_family'], self.config['font_size']),
            bg=self.config['bg_color'],
            fg=self.config['text_color'],
            insertbackground=self.config['accent_color'],
            selectbackground=self.config['accent_color'],
            selectforeground='white',
            state=tk.DISABLED,
            relief=tk.FLAT,
            borderwidth=0
        )
        self.text_widget.pack(expand=True, fill=tk.BOTH)
        
        # Configure text tags for different types of content
        self.text_widget.tag_config('timestamp', foreground=self.config['timestamp_color'], font=(self.config['font_family'], 9))
        self.text_widget.tag_config('transcript', foreground=self.config['text_color'])
        self.text_widget.tag_config('memory', foreground=self.config['memory_color'], font=(self.config['font_family'], self.config['font_size'], 'bold'))
        self.text_widget.tag_config('status', foreground=self.config['accent_color'], font=(self.config['font_family'], 10, 'italic'))
    
    def _create_control_buttons(self, parent):
        """Create control buttons for additional functionality."""
        button_frame = ttk.Frame(parent, style='Dark.TFrame')
        button_frame.pack(fill=tk.X)
        
        # Clear button
        clear_btn = tk.Button(
            button_frame,
            text="🗑️ Clear",
            command=self._clear_transcript,
            bg=self.config['bg_color'],
            fg=self.config['text_color'],
            activebackground=self.config['accent_color'],
            activeforeground='white',
            relief=tk.FLAT,
            font=(self.config['font_family'], 9)
        )
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save button
        save_btn = tk.Button(
            button_frame,
            text="💾 Save",
            command=self._save_transcript,
            bg=self.config['bg_color'],
            fg=self.config['text_color'],
            activebackground=self.config['accent_color'],
            activeforeground='white',
            relief=tk.FLAT,
            font=(self.config['font_family'], 9)
        )
        save_btn.pack(side=tk.LEFT)
        
        # Font size controls
        font_frame = ttk.Frame(button_frame, style='Dark.TFrame')
        font_frame.pack(side=tk.RIGHT)
        
        tk.Button(
            font_frame,
            text="A-",
            command=self._decrease_font,
            bg=self.config['bg_color'],
            fg=self.config['text_color'],
            activebackground=self.config['accent_color'],
            activeforeground='white',
            relief=tk.FLAT,
            font=(self.config['font_family'], 8),
            width=3
        ).pack(side=tk.LEFT)
        
        tk.Button(
            font_frame,
            text="A+",
            command=self._increase_font,
            bg=self.config['bg_color'],
            fg=self.config['text_color'],
            activebackground=self.config['accent_color'],
            activeforeground='white',
            relief=tk.FLAT,
            font=(self.config['font_family'], 8),
            width=3
        ).pack(side=tk.LEFT)
    
    def _check_queue(self):
        """Check for UI updates from the main thread."""
        try:
            while True:
                update_type, data = self.ui_queue.get_nowait()
                
                if update_type == 'transcript':
                    self._add_transcript_text(data)
                elif update_type == 'memory':
                    self._add_memory_notification(data)
                elif update_type == 'status':
                    self._update_status(data)
                    
        except queue.Empty:
            pass
        
        # Schedule next check
        if self.root:
            self.root.after(100, self._check_queue)
    
    def _add_transcript_text(self, transcript_data):
        """Add transcript text to the display."""
        if not self.text_widget:
            return
            
        timestamp = transcript_data.get('timestamp', datetime.now().strftime("%H:%M:%S"))
        text = transcript_data.get('text', '')
        
        self.text_widget.config(state=tk.NORMAL)
        
        # Add timestamp
        self.text_widget.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        
        # Add transcript text
        self.text_widget.insert(tk.END, f"{text}\n", 'transcript')
        
        # Auto-scroll to bottom
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
        
        self.transcript_count += 1
    
    def _add_memory_notification(self, memory_data):
        """Add memory creation notification."""
        if not self.text_widget:
            return
            
        category = memory_data.get('category', 'note')
        text = memory_data.get('text', '')
        
        self.text_widget.config(state=tk.NORMAL)
        
        # Add memory notification
        memory_text = f"    🧠 Memory Created ({category}): {text}\n"
        self.text_widget.insert(tk.END, memory_text, 'memory')
        
        # Auto-scroll to bottom
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
        
        self.memory_count += 1
        self.memory_label.config(text=f"💾 Memories: {self.memory_count}")
    
    def _update_status(self, status_text):
        """Update the status label."""
        if self.status_label:
            self.status_label.config(text=status_text)
    
    def _clear_transcript(self):
        """Clear all transcript text."""
        if self.text_widget:
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.config(state=tk.DISABLED)
            self.transcript_count = 0
            self.memory_count = 0
            self.memory_label.config(text="💾 Memories: 0")
    
    def _save_transcript(self):
        """Save current transcript to file."""
        if not self.text_widget:
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"omi_transcript_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                content = self.text_widget.get(1.0, tk.END)
                f.write(content)
            
            # Show temporary status message
            original_status = self.status_label.cget('text')
            self.status_label.config(text=f"💾 Saved to {filename}")
            self.root.after(3000, lambda: self.status_label.config(text=original_status))
            
        except Exception as e:
            self.status_label.config(text=f"❌ Save failed: {str(e)}")
    
    def _increase_font(self):
        """Increase font size."""
        self.config['font_size'] = min(self.config['font_size'] + 1, 20)
        self.text_widget.config(font=(self.config['font_family'], self.config['font_size']))
    
    def _decrease_font(self):
        """Decrease font size."""
        self.config['font_size'] = max(self.config['font_size'] - 1, 8)
        self.text_widget.config(font=(self.config['font_family'], self.config['font_size']))
    
    def _on_closing(self):
        """Handle window closing."""
        print("🚪 UI window closing...")
        self.running = False
        if self.root:
            self.root.quit()
            self.root.destroy()
            self.root = None
    
    # Public methods for external use
    def update_transcript(self, transcript_text):
        """Add new transcript text to the window."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.ui_queue.put(('transcript', {
            'text': transcript_text,
            'timestamp': timestamp
        }))
    
    def update_memory(self, category, text):
        """Add memory creation notification."""
        self.ui_queue.put(('memory', {
            'category': category,
            'text': text
        }))
    
    def update_status(self, status_text):
        """Update the status display."""
        self.ui_queue.put(('status', status_text))
    
    def is_running(self):
        """Check if the UI window is still running."""
        return self.running and self.root is not None
