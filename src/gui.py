# TEAM_001: Provides a Graphical User Interface for the Moon+ to KOReader migration tool.
import customtkinter as ctk
import tkinter.filedialog as filedialog
import threading
import sys
import os

from src.main import run_migration

class MigrationApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Moon+ to KOReader Migration Tool")
        self.geometry("600x480")
        
        # Configure grid mapping
        self.grid_columnconfigure(1, weight=1)
        
        # Title Header
        self.title_label = ctk.CTkLabel(self, text="Moon+ to KOReader Migrator", font=ctk.CTkFont(size=22, weight="bold"))
        self.title_label.grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 15))
        
        # Input Selection
        self.in_label = ctk.CTkLabel(self, text="Moon+ Backup (.mrpro):")
        self.in_label.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.in_path_var = ctk.StringVar()
        self.in_entry = ctk.CTkEntry(self, textvariable=self.in_path_var)
        self.in_entry.grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ew")
        self.in_btn = ctk.CTkButton(self, text="Browse", command=self.browse_input)
        self.in_btn.grid(row=1, column=2, padx=20, pady=10)
        
        # Output Selection
        self.out_label = ctk.CTkLabel(self, text="Output Folder:")
        self.out_label.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        self.out_path_var = ctk.StringVar()
        self.out_entry = ctk.CTkEntry(self, textvariable=self.out_path_var)
        self.out_entry.grid(row=2, column=1, padx=(0, 10), pady=10, sticky="ew")
        self.out_btn = ctk.CTkButton(self, text="Browse", command=self.browse_output)
        self.out_btn.grid(row=2, column=2, padx=20, pady=10)
        
        # Options (EPUBs and Replacements)
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=3, column=0, columnspan=3, padx=20, pady=15, sticky="ew")
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_columnconfigure(1, weight=1)
        
        self.extract_epubs_var = ctk.BooleanVar(value=True)
        self.epubs_chk = ctk.CTkCheckBox(self.options_frame, text="Extract EPUBs", variable=self.extract_epubs_var)
        self.epubs_chk.grid(row=0, column=0, padx=20, pady=15)
        
        self.extract_replacements_var = ctk.BooleanVar(value=True)
        self.replacements_chk = ctk.CTkCheckBox(self.options_frame, text="Extract Text Replacements", variable=self.extract_replacements_var)
        self.replacements_chk.grid(row=0, column=1, padx=20, pady=15)
        
        # Progress and Status Label
        self.status_var = ctk.StringVar(value="Status: Ready.")
        self.status_label = ctk.CTkLabel(self, textvariable=self.status_var, font=ctk.CTkFont(size=13))
        self.status_label.grid(row=4, column=0, columnspan=3, padx=20, pady=(5, 5))
        
        self.progressbar = ctk.CTkProgressBar(self)
        self.progressbar.grid(row=5, column=0, columnspan=3, padx=20, pady=(0, 15), sticky="ew")
        self.progressbar.set(0)
        
        # Execution Button
        self.run_btn = ctk.CTkButton(self, text="Start Migration", command=self.start_migration, fg_color="green", hover_color="darkgreen", height=40)
        self.run_btn.grid(row=6, column=0, columnspan=3, padx=20, pady=10, sticky="ew")
        
    def browse_input(self):
        filename = filedialog.askopenfilename(title="Select Moon+ Backup", filetypes=[("Moon+ Backup Files", "*.mrpro")])
        if filename:
            self.in_path_var.set(filename)
            
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.out_path_var.set(directory)
            
    def start_migration(self):
        in_path = self.in_path_var.get()
        out_path = self.out_path_var.get()
        
        if not in_path or not out_path:
            self.status_var.set("Error: Please select both an input file and output directory.")
            return
            
        self.run_btn.configure(state="disabled")
        self.progressbar.set(0)
        
        # Run backend code in a background thread to prevent tkinter from freezing
        thread = threading.Thread(
            target=self.run_migration_thread, 
            args=(in_path, out_path, self.extract_epubs_var.get(), self.extract_replacements_var.get())
        )
        thread.start()
        
    def run_migration_thread(self, in_path, out_path, ext_epubs, ext_reps):
        def update_status(msg):
            # Safe cross-thread updating
            self.after(0, self.status_var.set, f"Status: {msg}")
            
        def update_progress(current, total):
            if total > 0:
                prog = current / total
                self.after(0, self.progressbar.set, prog)
                self.after(0, self.status_var.set, f"Extracting EPUBs: {current}/{total} ({(prog*100):.1f}%)")
        
        try:
            run_migration(in_path, out_path, ext_epubs, ext_reps, status_cb=update_status, progress_cb=update_progress)
            update_status("Migration completed successfully!")
            self.after(0, self.progressbar.set, 1.0)
        except Exception as e:
            update_status(f"Error: {str(e)}")
        finally:
            self.after(0, self.run_btn.configure, {"state": "normal"})


def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    app = MigrationApp()
    app.mainloop()


if __name__ == "__main__":
    main()
