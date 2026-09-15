import os
import pandas as pd
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

def excel_date_to_string(serial):
    """Converts Excel serial date to YYYY-MM-DD."""
    try:
        # If Pandas already converted it to a datetime object
        if hasattr(serial, 'strftime'):
            return serial.strftime('%Y-%m-%d')
        
        if isinstance(serial, (int, float)):
            # Excel's base date is Dec 30, 1899
            dt = datetime(1899, 12, 30) + timedelta(days=serial)
            return dt.strftime('%Y-%m-%d')
        
        return str(serial)
    except:
        return None

def excel_time_to_hhmm(serial):
    """Converts Excel serial time to HH:MM."""
    try:
        if isinstance(serial, (int, float)):
            total_seconds = round(serial * 24 * 3600)
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            return f"{int(hours):02d}:{int(minutes):02d}"
        return str(serial)
    except:
        return ""

def main():
    folder_path = r"C:/Users/cescalantecastillo/Documents/MyDocs/autocontrolesISO+/Mai/plat"
    output_csv = "output_plat.csv"
    
    results = []
    file_count = 0

    # Walk through directory recursively
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".xlsx"):
                file_count += 1
                file_path = os.path.join(root, file)
                
                try:
                    # Using openpyxl engine via pandas to read specific cells
                    # We load the data once to avoid repeated disk reads
                    df_all = pd.read_excel(file_path, sheet_name='Plat', header=None, engine='openpyxl')
                    
                    # Extract Header Info (Adjusting for 0-based indexing: B5 is [4, 1])
                    raw_date = df_all.iloc[4, 1]  # B5
                    raw_of = df_all.iloc[5, 1]    # B6
                    thick = df_all.iloc[5, 6]     # G6
                    prov = df_all.iloc[4, 20]     # U5

                    date_str = excel_date_to_string(raw_date)

                    # Row Logic: Rows 13 to 77 (0-indexed 12 to 76)
                    heure_str, poids, davecp = "", "", ""
                    dcal, dnf = 0.0, 0.0
                    has_start = False

                    for row_idx in range(12, 77):
                        val_a = df_all.iloc[row_idx, 0]  # Col A
                        val_o = df_all.iloc[row_idx, 14] # Col O
                        val_m = df_all.iloc[row_idx, 12] # Col M
                        val_n = df_all.iloc[row_idx, 13] # Col N

                        # Check if A is not empty
                        if pd.notna(val_a) and str(val_a).strip() != "":
                            heure_str = excel_time_to_hhmm(val_a)
                            dcal = float(val_o) if pd.api.types.is_number(val_o) else 0.0
                            poids = str(val_m) if pd.notna(val_m) else ""
                            davecp = str(val_n) if pd.notna(val_n) else ""
                            has_start = True
                            continue

                        # If A is empty but O is not (and we had a start row)
                        if has_start and pd.notna(val_o) and str(val_o).strip() != "":
                            dnf = float(val_o)
                            
                            if dcal != 0:
                                dif = (dcal - dnf) / dcal * 100.0
                                
                                results.append({
                                    "Date": date_str,
                                    "OF": raw_of,
                                    "Heure": heure_str,
                                    "Épaisseur": thick,
                                    "Poids": poids,
                                    "Davecp": davecp,
                                    "Dsansp": dnf,
                                    "Dcalcul": dcal,
                                    "%Dif(calcul-sansp)": dif,
                                    "Fournisseur": prov
                                })
                
                except Exception as e:
                    print(f"Error processing file {file}: {e}")

    # Write to CSV
    if results:
        final_df = pd.DataFrame(results)
        # Convert the Date column to datetime and then back to a formatted string
        final_df['Date'] = pd.to_datetime(final_df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        final_df['Davecp'] = final_df['Davecp'].round(2)
        final_df['Dsansp'] = final_df['Dsansp'].round(2)
        final_df['Dcalcul'] = final_df['Dcalcul'].round(2)
        final_df['%Dif(calcul-sansp)'] = final_df['%Dif(calcul-sansp)'].round(4)
        final_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    
    print(f"Found {file_count} Excel files.")
    print(f"CSV written to {output_csv}")

if __name__ == "__main__":
    main()