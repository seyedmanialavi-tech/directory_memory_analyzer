import os
import tkinter as tk
from tkinter import filedialog, ttk
import threading

"""
File Scanner Application
A simple GUI tool to find and display large files in a selected directory
"""

class FileScanner:
    """Main application class for scanning and displaying large files"""
    
    def __init__(self):
        """Initialize the main window and setup UI components"""
        self.root = tk.Tk()
        self.root.title("File Scanner")
        self.root.geometry("900x500")
        self.root.configure(bg='white')
        self.scanning = False
        self.setup_ui()
        
    def setup_ui(self):
        """Create and arrange all user interface elements"""
        # Top section for folder selection
        top = tk.Frame(self.root, bg='white')
        top.pack(pady=10)
        
        tk.Label(top, text="Folder:", bg='white').pack(side='left')
        self.folder_var = tk.StringVar()
        tk.Entry(top, textvariable=self.folder_var, width=60).pack(side='left', padx=5)
        tk.Button(top, text="Browse", command=self.browse).pack(side='left')
        
        # Middle section for scan parameters
        mid = tk.Frame(self.root, bg='white')
        mid.pack(pady=5)
        
        tk.Label(mid, text="Min MB:", bg='white').pack(side='left')
        self.size_var = tk.StringVar(value="100")
        tk.Entry(mid, textvariable=self.size_var, width=8).pack(side='left', padx=5)
        
        tk.Label(mid, text="Top:", bg='white').pack(side='left')
        self.top_var = tk.StringVar(value="50")
        tk.Entry(mid, textvariable=self.top_var, width=8).pack(side='left', padx=5)
        
        self.scan_btn = tk.Button(mid, text="Scan", command=self.start_scan, bg='green', fg='white')
        self.scan_btn.pack(side='left', padx=10)
        
        self.stop_btn = tk.Button(mid, text="Stop", command=self.stop_scan, bg='red', fg='white', state='disabled')
        self.stop_btn.pack(side='left')
        
        # Status and progress indicators
        self.status = tk.Label(self.root, text="Ready", bg='white', fg='blue')
        self.status.pack()
        
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(fill='x', padx=10, pady=5)
        
        # Treeview for displaying results
        columns = ('#', 'Size', 'MB', 'Name', 'Path')
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=18)
        
        for col in columns:
            self.tree.heading(col, text=col)
        
        self.tree.column('#', width=40)
        self.tree.column('Size', width=90)
        self.tree.column('MB', width=70)
        self.tree.column('Name', width=200)
        self.tree.column('Path', width=420)
        
        # Add scrollbar for the treeview
        scroll = ttk.Scrollbar(self.root, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side='left', fill='both', expand=True, padx=10)
        scroll.pack(side='right', fill='y')
        
        # Info label for summary statistics
        self.info = tk.Label(self.root, text="", bg='white', fg='green')
        self.info.pack(pady=5)
        
    def browse(self):
        """Open directory selection dialog and set the folder path"""
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)
            
    def start_scan(self):
        """Validate inputs and start the scanning process in a separate thread"""
        folder = self.folder_var.get()
        if not folder or not os.path.exists(folder):
            return
            
        try:
            min_size = float(self.size_var.get())
            top_n = int(self.top_var.get())
        except:
            return
            
        self.clear_results()
        self.scanning = True
        self.scan_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.progress.start()
        self.status.config(text="Scanning...")
        
        # Run scan in background thread to keep UI responsive
        thread = threading.Thread(target=self.scan, args=(folder, min_size, top_n))
        thread.daemon = True
        thread.start()
        
    def scan(self, folder, min_mb, top_n):
        """Recursively scan directory and collect files above size threshold"""
        min_bytes = min_mb * 1024 * 1024
        results = []
        
        for root, dirs, files in os.walk(folder):
            if not self.scanning:
                break
            for file in files:
                try:
                    path = os.path.join(root, file)
                    size = os.path.getsize(path)
                    if size >= min_bytes:
                        results.append({
                            'path': path,
                            'size': size,
                            'size_mb': size / (1024*1024),
                            'name': file
                        })
                except:
                    pass
                    
        # Sort by size descending and limit to top N
        results.sort(key=lambda x: x['size'], reverse=True)
        results = results[:top_n]
        self.root.after(0, lambda: self.show_results(results))
        
    def show_results(self, results):
        """Display scan results in the treeview widget"""
        self.progress.stop()
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.scanning = False
        
        if not results:
            self.status.config(text="No files found")
            return
            
        total_size = 0
        for i, f in enumerate(results, 1):
            size_str = self.format_size(f['size'])
            self.tree.insert('', 'end', values=(i, size_str, f"{f['size_mb']:.1f}", f['name'], f['path']))
            total_size += f['size']
            
        self.info.config(text=f"Found: {len(results)} files | Total: {self.format_size(total_size)}")
        self.status.config(text="Done")
        
    def clear_results(self):
        """Remove all items from the treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.info.config(text="")
        
    def stop_scan(self):
        """Stop the ongoing scanning process"""
        self.scanning = False
        self.status.config(text="Stopped")
        self.progress.stop()
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        
    def format_size(self, size):
        """Convert bytes to human readable format (B, KB, MB, GB, TB)"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
        
    def run(self):
        """Start the main application loop"""
        self.root.mainloop()

if __name__ == "__main__":
    app = FileScanner()
    app.run()
