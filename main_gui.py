import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import os
import threading

class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Phase 1: Image-to-Word Converter")
        self.root.geometry("600x400")
        self.root.configure(bg="#f4f5f7")
        
        # Styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background="#f4f5f7")
        style.configure('TLabel', background="#f4f5f7", font=("Helvetica", 11))
        style.configure('TButton', font=("Helvetica", 10, "bold"), background="#4a90e2", foreground="white")
        style.map('TButton', background=[('active', '#357abd')])
        style.configure('Header.TLabel', font=("Helvetica", 16, "bold"), foreground="#2c3e50")
        
        # Main Frame
        main_frame = ttk.Frame(root, padding="30 30 30 30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header = ttk.Label(main_frame, text="Document Digitization MVP", style="Header.TLabel")
        header.pack(pady=(0, 20))
        
        # File Selection
        self.file_path_var = tk.StringVar(value="No file selected...")
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_label = ttk.Label(file_frame, textvariable=self.file_path_var, foreground="#7f8c8d", width=45)
        self.file_label.pack(side=tk.LEFT, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse Image", command=self.browse_file)
        browse_btn.pack(side=tk.RIGHT)
        
        # Settings
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(settings_frame, text="Processing Engine:").pack(side=tk.LEFT)
        self.engine_var = tk.StringVar(value="handwritten")
        ttk.Radiobutton(settings_frame, text="Handwritten (Paddle)", variable=self.engine_var, value="handwritten").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(settings_frame, text="Printed (Tesseract)", variable=self.engine_var, value="printed").pack(side=tk.LEFT)

        self.ai_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="Phase 2: Agentic System", variable=self.ai_var).pack(side=tk.LEFT, padx=20)
        
        # Progress & Action
        self.status_var = tk.StringVar(value="Ready.")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("Helvetica", 10, "italic"))
        self.status_label.pack(pady=10)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.pack(pady=10)
        
        self.run_btn = ttk.Button(main_frame, text="Generate Word Document", command=self.run_pipeline)
        self.run_btn.pack(pady=20, ipadx=20, ipady=5)

    def browse_file(self):
        filetypes = [("Image files", "*.jpg *.jpeg *.png")]
        filepath = filedialog.askopenfilename(title="Select an Image", filetypes=filetypes)
        if filepath:
            self.file_path_var.set(filepath)
            
    def run_pipeline(self):
        filepath = self.file_path_var.get()
        if not os.path.exists(filepath) or filepath == "No file selected...":
            messagebox.showerror("Error", "Please select a valid image file first.")
            return
            
        self.run_btn.state(['disabled'])
        self.progress.start(15)
        self.status_var.set("Engine running... Analyzing layout and formatting...")
        
        # Run OCR in background thread to prevent UI freezing
        thread = threading.Thread(target=self._execute_pipeline, args=(filepath,))
        thread.start()
        
    def _execute_pipeline(self, filepath):
        engine = self.engine_var.get()
        use_ai = self.ai_var.get()
        
        try:
            # We call our optimized python pipeline natively via subprocess
            # To ensure standard output formats correctly
            if use_ai:
                cmd = ["python", "agentic_pipeline.py", filepath]
            else:
                cmd = ["python", "ocr_pipeline.py", filepath, "--type", engine]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            output, _ = process.communicate()
            
            self.root.after(0, self._process_complete, process.returncode, output)
            
        except Exception as e:
            self.root.after(0, self._process_complete, 1, str(e))
            
    def _process_complete(self, returncode, output):
        self.progress.stop()
        self.run_btn.state(['!disabled'])
        
        if returncode == 0 and "[ERROR]" not in output:
            self.status_var.set("Success! Document generated.")
            messagebox.showinfo("Complete", f"Word Document successfully created!\n\nCheck the same folder as your image.")
        else:
            self.status_var.set("An error occurred.")
            messagebox.showerror("Execution Error", f"The pipeline failed to process the document.\n\nLogs:\n{output[-500:]}")

if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()
