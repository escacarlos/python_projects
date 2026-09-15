from datetime import datetime, timedelta
from load_liberation import load_liberation_data
import pandas as pd
import openpyxl
import os

def analyze_extract(folder_path, liberation_path, output_filename):
    count_lines = 0
    count_files = 0
    same_date = 0
    roll_over = 0
    roll_under = 0
    lines_in_file = 0
    try:
        records = []
        liberation_data = load_liberation_data(liberation_path)

        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith(('.xlsx', '.xls')):
                    try:
                        file_path = os.path.join(root, file)
                        date_str = file[:10]  # YYYY-MM-DD
                        of_number = os.path.splitext(file)[0][-5:]  # last 5 digits before extension

                        if of_number not in liberation_data:
                            print(f"{file}: OF number {of_number} not found in Liberation file.")
                            continue

                        lot_number, tiret, description, t_min, t_max, date, test_qc = liberation_data[of_number]
                        date_str1 = date.strftime("%Y-%m-%d")

                        wb = openpyxl.load_workbook(file_path, data_only=True)
                        sheet = wb["HD 4x3 (2)"]
                        
                        product_code = sheet['G5'].value                       

                        previous_hour = None
                        # current_date = datetime.strptime(date_str, "%Y-%m-%d")
                        current_date = datetime.strptime(date_str1, "%Y-%m-%d")
                        adjusted_datetime = None

                        for i in range(13, 76):
                            lines_in_file += 1
                            hour = sheet[f"A{i}"].value
                            hour_str = str(hour).strip() if pd.notna(hour) else ""

                            thickness_T1 = sheet[f"B{i}"].value
                            thickness_T2 = sheet[f"C{i}"].value
                            thickness_T3 = sheet[f"D{i}"].value
                            density = sheet[f"N{i}"].value  
                            width1 = sheet[f"G{i}"].value 
                            width2 = sheet[f"H{i}"].value 
                            length1 = sheet[f"J{i}"].value 
                            length2 = sheet[f"K{i}"].value

                            if hour is not None:
                                facer = 1
                                if hour_str:
                                    try:
                                        current_hour = parse_time_flexibly(hour_str)
                                        if previous_hour and previous_hour > current_hour:
                                            roll_over += 1
                                        previous_hour = current_hour

                                        adjusted_datetime = datetime.combine(current_date.date(), current_hour)

                                    except ValueError:
                                        continue  # Invalid time, skip row
                            else:
                                continue

                            if adjusted_datetime is None:
                                print(f"Skipping row in file {file} due to invalid or missing time at line {i}")
                                continue

                            records.append([
                                lot_number,
                                tiret,
                                of_number,
                                product_code,
                                description,
                                adjusted_datetime,
                                thickness_T1,
                                thickness_T2,
                                thickness_T3,
                                width1,
                                width2,
                                length1,
                                length2,
                                density,
                                facer,                            
                            ])

                            count_lines += 1
                    except Exception as fe:
                        print(f"Failed to read {file_path}: {fe}")
                    count_files += 1

        if records:
            output_dir = os.path.dirname(folder_path.rstrip("/\\"))
            output_csv = os.path.join(output_dir, output_filename)
            df = pd.DataFrame(records, columns=[
                "LotNumber", "tiret", "OF", "Product_code", "Description", "TimeStamp",
                "Thickness_T1", "Thickness_T2", "Thickness_T3", "Width1", "Width2",
                "Length1", "Length2", "Density", "Facer"
            ])
            df.to_csv(output_csv, index=False)
            print(f"Autocontrole data saved as: {output_csv}")
            print(f"{count_files} files processed, {count_lines} lines written, {lines_in_file} lines read, {same_date} same date, {roll_over} roll over and {roll_under} roll under")
        else:
            print("No valid data found in the provided folder.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def parse_time_flexibly(time_str):
    for fmt in ("%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized time format: {time_str}")
