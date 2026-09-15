import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import threading
import time
from time import perf_counter

from processor import *
from plotting import *

########################
# GLOBAL VARIABLES
db_file = None
excel_file = None
csv_file = None
csv_file_final = None
working = False
########################

def browse_file():
    global db_file
    db_file = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.db")])


def browse_csv():
    global csv_file
    csv_file = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not csv_file:
        messagebox.showwarning("No File", "No CSV file selected.")

def browse_excel():
    global excel_file
    excel_file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    if not excel_file:
        messagebox.showwarning("No File", "No Excel file selected.")

def load_csv_final():
    global csv_file_final, final_df
    csv_file_final = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if not csv_file_final:
        messagebox.showwarning("No File", "No CSV file selected.")
        return

    final_df = pd.read_csv(csv_file_final)
    log(f"Final CSV loaded with {len(final_df)} rows.")

    # Populate dropdown with unique sorted Nominal Thickness Max values
    unique_nominals = sorted(final_df['Nominal Thickness Max'].dropna().unique())
    product_codes = sorted(final_df['ProductCode'].dropna().unique())
    nominal_dropdown['values'] = unique_nominals
    product_dropdown['values'] = product_codes
    if unique_nominals:
        nominal_entry.set(unique_nominals[0])
        product_entry.set(product_codes[0])

def search_OF():
    global working
    working = True
    animate_loading()

    try:
        if not db_file or not os.path.exists(db_file):
            messagebox.showerror("Error", "Please select a Data Base file first.")
            return
        if not excel_file or not os.path.exists(excel_file):
            messagebox.showerror("Error", "Please select an Excel file first.")
            return
        
        global csv_file, csv_file_final

        start = perf_counter()
        if db_file:
            log("Processing Data Base...")
            csv_file = process_database(db_file, messagebox)

        if csv_file:  
            log("Fetching OF numbers in fichier liberation...")
            enriched_csv_path = search_OF_number(csv_file, excel_file, messagebox)

        if enriched_csv_path:
            log("Enriching CSV with Autocontrole data...")
            csv_file_full = enrich_with_autocontrole(enriched_csv_path, messagebox)
            log("Adding error columns...")
            csv_file_final = add_error_columns_to_csv(csv_file_full, messagebox)    
            log(f"Finished enriching...")
            log("Cleaning up final file...")
            csv_file_final = clean_final_csv(csv_file_final)
            log(f"File saved as: {csv_file_final}")
            log(f"Processing finished successfully after {perf_counter() - start} seconds")    
    finally:
        working = False

def threaded_search_OF():
    threading.Thread(target=search_OF, daemon=True).start()

def log(text):
    output_text.insert(tk.END, text + "\n")
    output_text.see(tk.END)  # Auto-scroll
    output_text.update_idletasks()  # This forces the UI to refresh immediately

def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("About")
    about_window.geometry("320x150")
    about_text = """
Version: 0.3
Python: 3.13.2
Libraries: tkinter, sqlite3, pandas, os, matplotlib, openpyxl
Author: Carlos Alfredo Escalante Castillo
    """
    tk.Label(about_window, text=about_text, justify="left").pack(pady=20)

def animate_loading():
    def loop():
        dot_count = 0
        while working:
            dots = '.' * (dot_count % 4)
            loading_label.config(text=f"Processing{dots}")
            loading_label.update_idletasks()
            dot_count += 1
            time.sleep(0.5)  # delay between updates
        loading_label.config(text="")  # Clear when done
    threading.Thread(target=loop, daemon=True).start()
    
# Create GUI
root = tk.Tk()
root.title("Database Processor")
root.geometry("800x500")  # Wider to accommodate the side panel

# Create main frame with horizontal layout
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

# Left frame for controls
left_frame = tk.Frame(main_frame)
left_frame.pack(side="left", fill="y", padx=10, pady=10)

# Right frame for text output
right_frame = tk.Frame(main_frame)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# ==== LEFT PANEL UI ====
tk.Label(left_frame, text="Select SQLite Database:").pack()
tk.Button(left_frame, text="Browse Database", command=browse_file).pack(pady=5)
tk.Label(left_frame, text="Select Excel Liberation OF file:").pack()
tk.Button(left_frame, text="Browse Excel file", command=browse_excel).pack(pady=5)

tk.Button(left_frame, text="Enrich CSV", command=threaded_search_OF).pack(pady=5)
loading_label = tk.Label(left_frame, text="", font=("Arial", 10))
loading_label.pack()

tk.Button(left_frame, text="Load final csv", command=load_csv_final).pack(pady=5)

tk.Label(left_frame, text="Enter Product Code:").pack()
product_entry = tk.StringVar()
product_dropdown = ttk.Combobox(left_frame, textvariable=product_entry, state="readonly")
product_dropdown.pack()
tk.Button(left_frame, text="Plot by Product Code", command=lambda: plot_pc(csv_file_final, messagebox, os, pd, product_entry, log)).pack(pady=5)

tk.Label(left_frame, text="Select Nominal Thickness Max:").pack()
nominal_entry = tk.StringVar()
nominal_dropdown = ttk.Combobox(left_frame, textvariable=nominal_entry, state="readonly")
nominal_dropdown.pack()
tk.Button(left_frame, text="Plot by Nominal Thickness", command=lambda: plot_by_nominal_dropdown(final_df, nominal_entry, log)).pack(pady=5)

nominal_entry_2 = nominal_dropdown
nominal_entry_2.pack()
tk.Button(left_frame, text="Dispersion Plot by Nominal Thickness", command=lambda: plot_nt(csv_file_final, messagebox, os, pd, nominal_entry)).pack(pady=5)

nominal_entry_3 = nominal_dropdown
nominal_entry_3.pack()
tk.Button(left_frame, text="Another Plot by Nominal Thickness", command=lambda: plot_nt_max(csv_file_final, messagebox, os, pd, nominal_entry)).pack(pady=5)

tk.Button(left_frame, text="About", command=show_about).pack(side="bottom", pady=10)

# ==== RIGHT PANEL TEXT OUTPUT ====
output_text = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD, width=60, height=30)
output_text.pack(fill="both", expand=True)

# You can use this widget to insert logs like:
# output_text.insert(tk.END, "Loaded 10 Excel files...\n")

root.mainloop()