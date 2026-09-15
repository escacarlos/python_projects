import sqlite3
import pandas as pd
import os
import openpyxl
import re

def process_database(db_file, messagebox):
    try:
        conn = sqlite3.connect(db_file)
        query = """
            SELECT
                req.ProductCode,
                res.InsulatorDensity,
                res.TotalThickness,
                req.Timestamp
            FROM Requests req
            INNER JOIN Results res ON res.RequestId = req.RequestId
            WHERE req.Length IS NOT NULL
        """
        df = pd.read_sql_query(query, conn)
        conn.close()

        # Format timestamp
        df['Date'] = pd.to_datetime(df['Timestamp']).dt.strftime('%Y-%m-%d')

        # Ensure numeric values for aggregation
        df['InsulatorDensity'] = pd.to_numeric(df['InsulatorDensity'], errors='coerce')
        df['TotalThickness'] = pd.to_numeric(df['TotalThickness'], errors='coerce')
        
        # Drop NaN values before grouping
        df.dropna(subset=['InsulatorDensity', 'TotalThickness'], inplace=True)

        # Filter out entries with density < 25.5 and > 31.5
        df = df[df['InsulatorDensity'] >= 25.5]

        # df = df[df['InsulatorDensity'] <= 31.5]

        # Compute daily averages per ProductCode
        avg_df = df.groupby(['ProductCode', 'Date'], as_index=False).agg({
            'InsulatorDensity': 'mean',
            'TotalThickness': 'mean'
        })
        avg_df.rename(columns={
            'InsulatorDensity': 'Density',
            'TotalThickness': 'Thickness'
        }, inplace=True)

        # Save to CSV
        output_file = os.path.join(os.path.dirname(db_file), "database_AVERAGE.csv")
        avg_df.to_csv(output_file, index=False)
        # messagebox.showinfo("Success", f"Processed data base, file saved as: {output_file}")
        return output_file

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred processing the data base: {str(e)}")

def search_OF_number(csv_file, excel_file, messagebox):
    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        df['OF#'] = ""  # Add empty OF# column
        df['Description'] = ""
        df['Nominal Thickness Min'] = ""
        df['Nominal Thickness Max'] = ""

        # Load Excel workbook
        wb = openpyxl.load_workbook(excel_file, data_only=True)
        ws = wb.active  # Assumes data is in the first sheet

        # Iterate over rows in CSV
        for idx, row in df.iterrows():
            csv_code = str(row['ProductCode']).strip()
            csv_date = pd.to_datetime(row['Date']).strftime('%Y-%m-%d')

            # Scan Excel rows (skip header, assume starts at row 2)
            for excel_row in ws.iter_rows(min_row=2):
                excel_code = str(excel_row[3].value).strip() if excel_row[3].value else ""
                excel_date = excel_row[8].value

                if not excel_date or not excel_code:
                    continue

                # Format Excel date
                try:
                    formatted_excel_date = pd.to_datetime(excel_date).strftime('%Y-%m-%d')
                except:
                    continue  # Skip badly formatted dates

                if excel_code == csv_code and formatted_excel_date == csv_date:
                    of_number = str(excel_row[2].value).strip() if excel_row[2].value else ""
                    description = str(excel_row[4].value).strip() if excel_row[4].value else ""
                    thickness_min = excel_row[5].value if excel_row[5].value else ""
                    thickness_max = excel_row[6].value if excel_row[6].value else ""

                    df.at[idx, 'OF#'] = of_number
                    df.at[idx, 'Description'] = description
                    df.at[idx, 'Nominal Thickness Min'] = thickness_min
                    df.at[idx, 'Nominal Thickness Max'] = thickness_max    
                    break  # Stop after first match

        # Ensure Date is datetime for sorting and comparison
        df['Date'] = pd.to_datetime(df['Date'])

        # Sort by ProductCode and Date
        df.sort_values(by=['ProductCode', 'Date'], inplace=True)

        # Fill missing OF# if the next day has it (within same ProductCode)
        for i in range(len(df) - 1):
            current = df.iloc[i]
            next_row = df.iloc[i + 1]
            if (
                current['OF#'] == "" and
                current['ProductCode'] == next_row['ProductCode'] and
                (next_row['Date'] - current['Date']).days == 1 and
                next_row['OF#'] != ""
            ):
                df.at[df.index[i], 'OF#'] = next_row['OF#']
                df.at[df.index[i], 'Description'] = next_row['Description']
                df.at[df.index[i], 'Nominal Thickness Min'] = next_row['Nominal Thickness Min']
                df.at[df.index[i], 'Nominal Thickness Max'] = next_row['Nominal Thickness Max']

        # Save enriched CSV
        enriched_csv = csv_file.replace(".csv", "_ENRICHED.csv")
        df.to_csv(enriched_csv, index=False)
        # messagebox.showinfo("Success", f"Enriched CSV with liberation OF saved as: {enriched_csv}")
        return enriched_csv

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while enriching with liberation OF: {e}")

def enrich_with_autocontrole(enriched_csv_path, messagebox):
    try:
        df = pd.read_csv(enriched_csv_path)
        df['Autocontrole_Thickness'] = None
        df['Autocontrole_Density'] = None

        base_folder = os.path.dirname(enriched_csv_path)
        autocontrole_folder = os.path.join(base_folder, "Autocontrole")

        for idx, row in df.iterrows():
            try:
                of_number = str(int(float(row['OF#']))).zfill(5)
            except (ValueError, TypeError):
                of_number = ""

            match_file = None
            for root, dirs, files in os.walk(autocontrole_folder):
                for filename in files:
                    if filename.endswith(".xlsx"):
                        file_of = re.search(r'(\d{5})(?=\.xlsx$)', filename)
                        if file_of and file_of.group(1) == of_number:
                            match_file = os.path.join(root, filename)
                            break
                if match_file:
                    break

            if match_file:
                try:
                    wb = openpyxl.load_workbook(match_file, data_only=True)
                    try:
                        ws = wb["pré-emballage"]
                    except KeyError:
                        ws = wb.active

                    thickness_values = []
                    density_values = []

                    for i in range(13, 76):  # E13 to E75 and J13 to J75
                        a_val = ws[f"A{i}"].value
                        e_val = ws[f"E{i}"].value
                        j_val = ws[f"J{i}"].value

                        if a_val is not None:
                            if isinstance(e_val, (int, float)):
                                thickness_values.append(e_val)
                            if isinstance(j_val, (int, float)):
                                density_values.append(j_val)

                    avg_thickness = sum(thickness_values) / len(thickness_values) if thickness_values else 0
                    avg_density = sum(density_values) / len(density_values) if density_values else 0

                    df.at[idx, 'Autocontrole_Thickness'] = avg_thickness
                    df.at[idx, 'Autocontrole_Density'] = avg_density

                except Exception as read_err:
                    df.at[idx, 'Autocontrole_Thickness'] = 0
                    df.at[idx, 'Autocontrole_Density'] = 0
                    # print(f"Error reading file {match_file}: {read_err}")

        final_csv = enriched_csv_path.replace(".csv", "_FULL.csv")
        df.to_csv(final_csv, index=False)
        # messagebox.showinfo("Success", f"Final enriched CSV saved as: {final_csv}")
        return final_csv

    except Exception as e:
        messagebox.showerror("Error", f"Failed during autocontrole enrichment: {e}")

def add_error_columns_to_csv(csv_file, messagebox):
    try:
        if not csv_file or not os.path.exists(csv_file):
            messagebox.showerror("File Not Found", "Please select a CSV file first.")
            return

        df = pd.read_csv(csv_file)

        # Convert to numeric, ignoring non-numeric values
        df['Density'] = pd.to_numeric(df['Density'], errors='coerce')
        df['Autocontrole_Density'] = pd.to_numeric(df['Autocontrole_Density'], errors='coerce')
        df['Thickness'] = pd.to_numeric(df['Thickness'], errors='coerce')
        df['Autocontrole_Thickness'] = pd.to_numeric(df['Autocontrole_Thickness'], errors='coerce')

        # Calculate % error safely, avoiding division by zero
        df['%error_Density'] = ((df['Density'] - df['Autocontrole_Density']) / df['Density']) * 100
        df['%error_Thickness'] = ((df['Thickness'] - df['Autocontrole_Thickness']) / df['Thickness']) * 100

        # Optionally round to 2 decimal places
        df['%error_Density'] = df['%error_Density'].round(2)
        df['%error_Thickness'] = df['%error_Thickness'].round(2)

        # Save to the same file or to a new one
        output_file = csv_file.replace(".csv", "_with_errors.csv")
        df.to_csv(output_file, index=False)
        # messagebox.showinfo("Success", f"Processing ended succesfully.\nSaved as: {output_file}")
        return output_file
    
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred adding error columns: {e}")

def clean_final_csv(csv_path):
    # Load the final CSV file
    df = pd.read_csv(csv_path)

    # Drop rows where 'OF#' is null or empty
    df = df[df['OF#'].notna() & (df['OF#'].astype(str).str.strip() != "")]

    # Drop rows where 'Autocontrole_Thickness' is null or zero
    df = df[df['Autocontrole_Thickness'].notna() & (df['Autocontrole_Thickness'] != 0)]

    # Save cleaned file back to the same path or new one
    cleaned_path = os.path.splitext(csv_path)[0] + "_CLEANED.csv"
    df.to_csv(cleaned_path, index=False)

    # Delete intermediate files in the same directory
    base_dir = os.path.dirname(csv_path)
    files_to_delete = [
        "database_AVERAGE.csv",
        "database_AVERAGE_ENRICHED.csv",
        "database_AVERAGE_ENRICHED_FULL.csv",
        "database_AVERAGE_ENRICHED_FULL_with_errors.csv"
    ]
    for filename in files_to_delete:
        file_path = os.path.join(base_dir, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            # print(f"Deleted: {file_path}")

    # print(f"Cleaned file saved to: {cleaned_path}")
    return cleaned_path


