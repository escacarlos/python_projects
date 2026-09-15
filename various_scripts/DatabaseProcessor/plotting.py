import matplotlib.pyplot as plt

def plot_density(csv_file, messagebox, product_entry, os, pd):
    try:
        product_code = product_entry.get()
        if not product_code:
            messagebox.showerror("Invalid Input", "Please enter a Product Code.")
            return

        if not csv_file or not os.path.exists(csv_file):
            messagebox.showerror("File Not Found", "Please select a CSV file first.")
            return

        df = pd.read_csv(csv_file)
        df = df[df['ProductCode'].astype(str).str.strip() == product_code.strip()]

        if df.empty:
            messagebox.showinfo("No Data", f"No data found for Product Code {product_code}.")
            return

        df['Date'] = pd.to_datetime(df['Date'])
        df['Density'] = pd.to_numeric(df['Density'], errors='coerce')
        df['Autocontrole_Density'] = pd.to_numeric(df.get('Autocontrole_Density'), errors='coerce')

        plt.figure(figsize=(10, 5))
        
        # Plot main Density
        plt.scatter(df['Date'], df['Density'], color='blue', label='Measured Density', alpha=0.7)
        plt.plot(df['Date'], df['Density'], color='blue', linestyle='--', alpha=0.5)
        
        # Plot Autocontrole Density
        plt.scatter(df['Date'], df['Autocontrole_Density'], color='orange', label='Autocontrole Density', alpha=0.7, marker='x')
        plt.plot(df['Date'], df['Autocontrole_Density'], color='orange', linestyle='--', alpha=0.5)

        plt.xlabel("Date")
        plt.ylabel("Density")
        plt.title(f"Density Comparison for Product Code {product_code}")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        
        output_file = f"Density_{product_code}.png"
        plt.savefig(output_file, bbox_inches='tight')
        plt.show()
        plt.close()
        messagebox.showinfo("Success", f"Plot saved as {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def plot_thickness(csv_file, messagebox, product_entry, os, pd):
    try:
        product_code = product_entry.get()
        if not product_code:
            messagebox.showerror("Invalid Input", "Please enter a Product Code.")
            return

        if not csv_file or not os.path.exists(csv_file):
            messagebox.showerror("File Not Found", "Please select a CSV file first.")
            return

        df = pd.read_csv(csv_file)
        df = df[df['ProductCode'].astype(str).str.strip() == product_code.strip()]

        if df.empty:
            messagebox.showinfo("No Data", f"No data found for Product Code {product_code}.")
            return

        df['Date'] = pd.to_datetime(df['Date'])
        df['Thickness'] = pd.to_numeric(df['Thickness'], errors='coerce')
        df['Autocontrole_Thickness'] = pd.to_numeric(df.get('Autocontrole_Thickness'), errors='coerce')

        plt.figure(figsize=(10, 5))
        
        # Plot main Thickness
        plt.scatter(df['Date'], df['Thickness'], color='blue', label='Measured Thickness', alpha=0.7)
        plt.plot(df['Date'], df['Thickness'], color='blue', linestyle='--', alpha=0.5)
        
        # Plot Autocontrole Thickness
        plt.scatter(df['Date'], df['Autocontrole_Thickness'], color='orange', label='Autocontrole Thickness', alpha=0.7, marker='x')
        plt.plot(df['Date'], df['Autocontrole_Thickness'], color='orange', linestyle='--', alpha=0.5)

        plt.xlabel("Date")
        plt.ylabel("Thickness")
        plt.title(f"Thickness Comparison for Product Code {product_code}")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        
        output_file = f"Thickness_{product_code}.png"
        plt.savefig(output_file, bbox_inches='tight')
        plt.show()
        plt.close()
        messagebox.showinfo("Success", f"Plot saved as {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def plot_pc(csv_file_final, messagebox, os, pd, product_entry, log):
    if not csv_file_final or not os.path.exists(csv_file_final):
        messagebox.showerror("Error", "Please select a CSV file first.")
        return
    
    code = product_entry.get()
    log(f"Plotting product code: {code}")
    plot_density(csv_file_final, messagebox, product_entry, os, pd)
    plot_thickness(csv_file_final, messagebox, product_entry, os, pd)
    log("Plot completed.")

def plot_density_by_nominal_thickness(csv_file, messagebox, os, pd, nominal_entry):
    try:
        nominal_value = nominal_entry.get()
        if not nominal_value:
            messagebox.showerror("Invalid Input", "Please enter a Nominal Thickness Max value.")
            return

        if not csv_file or not os.path.exists(csv_file):
            messagebox.showerror("File Not Found", "Please select a CSV file first.")
            return

        df = pd.read_csv(csv_file)
        df['Nominal Thickness Max'] = pd.to_numeric(df['Nominal Thickness Max'], errors='coerce')
        df = df[df['Nominal Thickness Max'] == float(nominal_value)]

        if df.empty:
            messagebox.showinfo("No Data", f"No data found for Nominal Thickness Max = {nominal_value}.")
            return

        df['Date'] = pd.to_datetime(df['Date'])
        df['Density'] = pd.to_numeric(df['Density'], errors='coerce')
        df['Autocontrole_Density'] = pd.to_numeric(df['Autocontrole_Density'], errors='coerce')

        plt.figure(figsize=(10, 5))
        plt.scatter(df['Date'], df['Density'], color='blue', label='Measured Density', alpha=0.7)
        plt.plot(df['Date'], df['Density'], color='blue', linestyle='--', alpha=0.5)

        plt.scatter(df['Date'], df['Autocontrole_Density'], color='orange', label='Autocontrole Density', alpha=0.7, marker='x')
        plt.plot(df['Date'], df['Autocontrole_Density'], color='orange', linestyle='--', alpha=0.5)

        plt.xlabel("Date")
        plt.ylabel("Density")
        plt.title(f"Density Comparison for Nominal Thickness Max = {nominal_value}")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()

        output_file = f"Density_Nominal_{nominal_value}.png"
        plt.savefig(output_file, bbox_inches='tight')
        plt.show()
        plt.close()
        messagebox.showinfo("Success", f"Plot saved as {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def plot_thickness_by_nominal_thickness(csv_file, messagebox, os, pd, nominal_entry):
    try:
        nominal_value = nominal_entry.get()
        if not nominal_value:
            messagebox.showerror("Invalid Input", "Please enter a Nominal Thickness Max value.")
            return

        if not csv_file or not os.path.exists(csv_file):
            messagebox.showerror("File Not Found", "Please select a CSV file first.")
            return

        df = pd.read_csv(csv_file)
        df['Nominal Thickness Max'] = pd.to_numeric(df['Nominal Thickness Max'], errors='coerce')
        df = df[df['Nominal Thickness Max'] == float(nominal_value)]

        if df.empty:
            messagebox.showinfo("No Data", f"No data found for Nominal Thickness Max = {nominal_value}.")
            return

        df['Date'] = pd.to_datetime(df['Date'])
        df['Thickness'] = pd.to_numeric(df['Thickness'], errors='coerce')
        df['Autocontrole_Thickness'] = pd.to_numeric(df['Autocontrole_Thickness'], errors='coerce')

        plt.figure(figsize=(10, 5))
        plt.scatter(df['Date'], df['Thickness'], color='green', label='Measured Thickness', alpha=0.7)
        plt.plot(df['Date'], df['Thickness'], color='green', linestyle='--', alpha=0.5)

        plt.scatter(df['Date'], df['Autocontrole_Thickness'], color='purple', label='Autocontrole Thickness', alpha=0.7, marker='x')
        plt.plot(df['Date'], df['Autocontrole_Thickness'], color='purple', linestyle='--', alpha=0.5)

        plt.xlabel("Date")
        plt.ylabel("Thickness")
        plt.title(f"Thickness Comparison for Nominal Thickness Max = {nominal_value}")
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()

        output_file = f"Thickness_Nominal_{nominal_value}.png"
        plt.savefig(output_file, bbox_inches='tight')
        plt.show()
        plt.close()
        messagebox.showinfo("Success", f"Plot saved as {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def plot_nt(csv_file_final, messagebox, os, pd, nominal_entry):
    if not csv_file_final or not os.path.exists(csv_file_final):
        messagebox.showerror("Error", "Please select a CSV file first.")
        return
    plot_density_by_nominal_thickness(csv_file_final, messagebox, os, pd, nominal_entry)
    plot_thickness_by_nominal_thickness(csv_file_final, messagebox, os, pd, nominal_entry)

def plot_density_error_by_nominal_thickness_max(csv_file, selected_nominal_thickness_max, pd):
    df = pd.read_csv(csv_file)

    try:
        selected_nominal = float(selected_nominal_thickness_max.get())
    except ValueError:
        # log("Invalid selection.")
        return
    
    # Filter rows by selected Nominal Thickness Max
    filtered_df = df[df["Nominal Thickness Max"] == selected_nominal]

    if filtered_df.empty:
        print("No data found for the selected Nominal Thickness Max.")
        return

    x = range(len(filtered_df))  # Numeric index for plotting

    plt.figure(figsize=(10, 6))

    # Plot individual points
    plt.scatter(x, filtered_df["Density"], label="Density", color="blue")
    plt.scatter(x, filtered_df["Autocontrole_Density"], label="Autocontrole Density", color="orange")

    # Draw error lines between each pair
    for i in x:
        plt.plot([i, i],
                 [filtered_df.iloc[i]["Density"], filtered_df.iloc[i]["Autocontrole_Density"]],
                 color="gray", linestyle="dashed", linewidth=1)

    # Add labels
    plt.xticks(ticks=x, labels=filtered_df["Date"], rotation=45)
    plt.ylabel("Density")
    plt.title(f"Density vs Autocontrole Density (Nominal Thickness Max = {selected_nominal_thickness_max})")
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()

def plot_thickness_error_by_nominal_thickness_max(csv_file, selected_nominal_thickness_max, pd):
    df = pd.read_csv(csv_file)

    try:
        selected_nominal = float(selected_nominal_thickness_max.get())
    except ValueError:
        # log("Invalid selection.")
        return

    filtered_df = df[df["Nominal Thickness Max"] == selected_nominal]

    if filtered_df.empty:
        print("No data found for the selected Nominal Thickness Max.")
        return

    x = range(len(filtered_df))

    plt.figure(figsize=(10, 6))
    plt.scatter(x, filtered_df["Thickness"], label="Thickness", color="green")
    plt.scatter(x, filtered_df["Autocontrole_Thickness"], label="Autocontrole Thickness", color="red")

    for i in x:
        plt.plot([i, i],
                 [filtered_df.iloc[i]["Thickness"], filtered_df.iloc[i]["Autocontrole_Thickness"]],
                 color="gray", linestyle="dashed", linewidth=1)

    plt.xticks(ticks=x, labels=filtered_df["Date"], rotation=45)
    plt.ylabel("Thickness")
    plt.title(f"Thickness vs Autocontrole Thickness (Nominal Thickness Max = {selected_nominal_thickness_max})")
    plt.legend()
    plt.tight_layout()
    plt.grid(True)
    plt.show()

def plot_nt_max(csv_file_final, messagebox, os, pd, selected_nominal_thickness_max):
    if not csv_file_final or not os.path.exists(csv_file_final):
        messagebox.showerror("Error", "Please select a CSV file first.")
        return
    plot_density_error_by_nominal_thickness_max(csv_file_final, selected_nominal_thickness_max, pd)
    plot_thickness_error_by_nominal_thickness_max(csv_file_final, selected_nominal_thickness_max, pd)

def plot_by_nominal_dropdown(final_df, nominal_entry, log):
    if final_df is None:
        log("Please load the final CSV file first.")
        return

    try:
        selected_nominal = float(nominal_entry.get())
    except ValueError:
        log("Invalid selection.")
        return

    df_filtered = final_df[final_df['Nominal Thickness Max'] == selected_nominal]

    if df_filtered.empty:
        log(f"No data found for Nominal Thickness Max = {selected_nominal}")
        return

    log(f"Showing products with Nominal Thickness Max = {selected_nominal}:")

    # Unique product code + description
    unique_products = df_filtered[['ProductCode', 'Description']].drop_duplicates()
    for _, row in unique_products.iterrows():
        log(f"{row['ProductCode']} - {row['Description']}")

    # Plot Density Comparison
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    for _, row in df_filtered.iterrows():
        ax[0].plot([0, 1], [row['Density'], row['Autocontrole_Density']], marker='o', label=f"{row['ProductCode']}")
    ax[0].set_title("Density vs Autocontrole")
    ax[0].set_ylabel("Density")
    ax[0].set_xticks([0, 1])
    ax[0].set_xticklabels(["Main", "Autocontrole"])

    # Plot Thickness Comparison
    for _, row in df_filtered.iterrows():
        ax[1].plot([0, 1], [row['Thickness'], row['Autocontrole_Thickness']], marker='o', label=f"{row['ProductCode']}")
    ax[1].set_title("Thickness vs Autocontrole")
    ax[1].set_ylabel("Thickness")
    ax[1].set_xticks([0, 1])
    ax[1].set_xticklabels(["Main", "Autocontrole"])

    plt.tight_layout()
    plt.show()