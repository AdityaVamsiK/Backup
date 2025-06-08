import customtkinter as ctk
import os
from tkinter import filedialog
from Backup import print_directory_tree, directory_diff, update_backup, create_replica

class BackupGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Directory Backup Utility")
        self.geometry("425x500")
        self.resizable(False, False)

        # Outer frame
        self.outer_frame = ctk.CTkFrame(self, corner_radius=10, border_width=2)
        self.outer_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # Source Directory
        self.location_label = ctk.CTkLabel(self.outer_frame, text="Source Directory:", anchor='w')
        self.location_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.source_entry = ctk.CTkEntry(self.outer_frame, width=200)
        self.source_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.source_button = ctk.CTkButton(self.outer_frame, text="Browse", command=self.browse_source, width=60)
        self.source_button.grid(row=0, column=2, padx=5, pady=5)

        # Backup Directory
        self.backup_label = ctk.CTkLabel(self.outer_frame, text="Backup Directory:", anchor='w')
        self.backup_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.backup_entry = ctk.CTkEntry(self.outer_frame, width=200)
        self.backup_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.backup_button = ctk.CTkButton(self.outer_frame, text="Browse", command=self.browse_backup, width=60)
        self.backup_button.grid(row=1, column=2, padx=5, pady=5)

        # Divider
        ctk.CTkLabel(self.outer_frame, text="", height=2).grid(row=2, column=0, columnspan=3)

        # Actions Frame
        self.button_frame = ctk.CTkFrame(self.outer_frame, fg_color="transparent")
        self.button_frame.grid(row=3, column=0, columnspan=3, pady=5, padx=5, sticky="ew")

        ctk.CTkButton(self.button_frame, text="Show Tree", command=self.show_tree, width=90).pack(side="left", padx=2)
        ctk.CTkButton(self.button_frame, text="Directory Diff", command=self.show_diff, width=90).pack(side="left", padx=2)
        ctk.CTkButton(self.button_frame, text="Update Backup", command=self.run_backup, width=90).pack(side="left", padx=2)
        ctk.CTkButton(self.button_frame, text="Create Replica", command=self.create_replica_dir, width=90).pack(side="left", padx=2)

        # Divider
        ctk.CTkLabel(self.outer_frame, text="", height=2).grid(row=4, column=0, columnspan=3)

        # Output box
        self.output_text = ctk.CTkTextbox(self.outer_frame, width=360, height=230)
        self.output_text.grid(row=5, column=0, columnspan=3, padx=10, pady=5)

        # Bottom Buttons
        self.bottom_frame = ctk.CTkFrame(self.outer_frame, fg_color="transparent")
        self.bottom_frame.grid(row=6, column=0, columnspan=3, pady=(5, 10))

        ctk.CTkButton(self.bottom_frame, text="OK", width=80, command=self.quit).pack(side="left", padx=5)
        ctk.CTkButton(self.bottom_frame, text="Cancel", width=80, command=self.quit).pack(side="left", padx=5)

    def browse_source(self):
        path = filedialog.askdirectory()
        if path:
            self.source_entry.delete(0, 'end')
            self.source_entry.insert(0, path)

    def browse_backup(self):
        path = filedialog.askdirectory()
        if path:
            self.backup_entry.delete(0, 'end')
            self.backup_entry.insert(0, path)

    def show_tree(self):
        source = self.source_entry.get()
        if not os.path.isdir(source):
            self.output_text.insert('end', "Invalid source path.\n")
            return
        self.output_text.insert('end', f"Directory Tree of: {source}\n")
        self.capture_tree_output(source)

    def capture_tree_output(self, path):
        from io import StringIO
        import sys

        buffer = StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        print_directory_tree(path)
        sys.stdout = sys_stdout
        self.output_text.insert('end', buffer.getvalue())

    def show_diff(self):
        src = self.source_entry.get()
        dst = self.backup_entry.get()
        if not os.path.isdir(src) or not os.path.isdir(dst):
            self.output_text.insert('end', "Invalid directories.\n")
            return

        self.output_text.insert('end', "Checking directory differences...\n")
        diff = directory_diff(src, dst)
        for key, items in diff.items():
            self.output_text.insert('end', f"{key.replace('_', ' ').title()}:\n")
            for i in items:
                self.output_text.insert('end', f"    {i}\n")
        self.output_text.insert('end', "---Diff Complete---\n\n")

    def run_backup(self):
        src = self.source_entry.get()
        dst = self.backup_entry.get()
        if not os.path.isdir(src) or not os.path.isdir(dst):
            self.output_text.insert('end', "Invalid directories.\n")
            return

        self.output_text.insert('end', f"Updating backup from {src} to {dst}...\n")
        update_backup(src, dst)
        self.output_text.insert('end', "---Backup Updated---\n\n")

    def create_replica_dir(self):
        src = self.source_entry.get()
        dst = self.backup_entry.get()
        if not os.path.isdir(src):
            self.output_text.insert('end', "Invalid source directory.\n")
            return

        self.output_text.insert('end', f"Creating replica from {src} to {dst}...\n")
        create_replica(src, dst)
        self.output_text.insert('end', "---Replica Created---\n\n")

if __name__ == '__main__':
    app = BackupGUI()
    app.mainloop()
