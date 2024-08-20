import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Global variable to store the initial file list and backup directory
initial_file_list = {}
backup_directory = "backup_files"

# Function to style the buttons
def style_button(button):
    button.config(
        font=("Arial", 12, "bold"),
        bg="#283593",  # Dark blue background
        fg="white",  # White text
        activebackground="#1a237e",  # Darker blue when pressed
        relief=tk.RAISED,
        bd=3
    )

def index_files(directory):
    """Index files in the directory and create a backup."""
    file_list = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_list[file_path] = os.path.getmtime(file_path)

            # Backup the file
            backup_file_path = os.path.join(backup_directory, os.path.relpath(file_path, directory))
            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
            shutil.copy2(file_path, backup_file_path)

    return file_list

def scan_directory():
    """Scan the directory to detect deleted files."""
    global initial_file_list
    directory = filedialog.askdirectory()
    if not directory:
        return

    # Initial scan to index all files
    if not initial_file_list:
        initial_file_list = index_files(directory)
        results_text.insert(tk.END, "Initial scan complete. Files indexed and backed up.\n")
    else:
        # Scan again to detect deleted files
        current_file_list = index_files(directory)
        deleted_files = [file for file in initial_file_list if not os.path.exists(file)]
        
        results_text.delete(1.0, tk.END)
        if deleted_files:
            for file in deleted_files:
                results_text.insert(tk.END, f"Deleted: {file}\n")
        else:
            results_text.insert(tk.END, "No deleted files found.\n")

def recover_file():
    """Recover detected deleted files from the backup."""
    global initial_file_list
    directory = filedialog.askdirectory()
    if not directory:
        return

    # List of files that were initially scanned but are now missing
    deleted_files = [file for file in initial_file_list if not os.path.exists(file)]

    if not deleted_files:
        messagebox.showinfo("No Files to Recover", "There are no deleted files to recover.")
        return

    for file in deleted_files:
        # Construct the path in the backup directory
        relative_path = os.path.relpath(file, os.path.dirname(list(initial_file_list.keys())[0]))
        backup_file_path = os.path.join(backup_directory, relative_path)

        if os.path.exists(backup_file_path):
            # Restore to the original location
            recovered_file_path = file
            os.makedirs(os.path.dirname(recovered_file_path), exist_ok=True)
            shutil.copy2(backup_file_path, recovered_file_path)
            results_text.insert(tk.END, f"Recovered: {recovered_file_path}\n")
        else:
            results_text.insert(tk.END, f"Backup not found for: {file}\n")
            messagebox.showerror("Recovery Failed", f"Backup not found for: {file}")

# GUI Setup
root = tk.Tk()
root.title("Lost Data Retrieval System")
root.geometry("600x400")
root.config(bg="black")  # Dark grey background

frame = tk.Frame(root, bg="green")
frame.pack(pady=10)

# Scan Button
scan_button = tk.Button(frame, text="Scan for Lost Data", command=scan_directory)
style_button(scan_button)
scan_button.pack(pady=8)

# Recover Button
recover_button = tk.Button(frame, text="Recover Deleted Files", command=recover_file)
style_button(recover_button)
recover_button.pack(pady=8)

# ScrolledText for displaying results
results_text = scrolledtext.ScrolledText(root, height=15, width=60, bg="#eceff1", fg="black", font=("Arial", 10))
results_text.pack(pady=10)

# Ensure backup directory exists
os.makedirs(backup_directory, exist_ok=True)

root.mainloop()
