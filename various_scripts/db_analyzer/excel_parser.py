from datetime import datetime, timedelta
from db_lookup import lookup_from_db_load
from load_db import load_database
from load_liberation import load_liberation_data
import pandas as pd
import openpyxl
import os

def analyze_extract(folder_path, liberation_path, database_path, is_old_version, output_filename, PRODUCT_TIME_OFFSET = {}):
    default_time = 10
    count_lines = 0
    count_files = 0
    db_found = 0
    same_date = 0
    roll_over = 0
    roll_under = 0
    lines_in_file = 0
    try:
        records = []
        liberation_data = load_liberation_data(liberation_path)
        db_loaded = load_database(database_path)

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
                        
                        # if t_max > 4:
                        #     default_time = 20

                        flag = False
                        if date_str == date_str1:
                            same_date += 1
                            flag = True
                        # else:
                        #     print(f"{file}: OF number {of_number}")

                        wb = openpyxl.load_workbook(file_path, data_only=True)
                        sheet = wb.active
                        if is_old_version:
                            sheet = wb["pré-emballage"]
                        else:
                            sheet = wb["Plat"]
                        
                        product_code = sheet['G5'].value
                        
                        pente = 0
                        is_pente = False
                        if t_min is not None:
                            pente = 1
                            is_pente = True
                            if is_old_version:
                                sheet = wb["pré-emballage"]
                            else:
                                sheet = wb["Pente"]
                                product_code = sheet['F5'].value
                        
                        if (product_code == ""):
                            product_code = fall_back_sheet(wb, product_code, ["SL", "HD 4x3 (2)", "Emball ISO"])

                        previous_hour = None
                        # current_date = datetime.strptime(date_str, "%Y-%m-%d")
                        current_date = datetime.strptime(date_str1, "%Y-%m-%d")
                        adjusted_datetime = None

                        for i in range(13, 76):
                            lines_in_file += 1
                            hour = sheet[f"A{i}"].value
                            hour_str = str(hour).strip() if pd.notna(hour) else ""
                            thickness_T1 = sheet[f"B{i}"].value
                            thickness_Milieu = sheet[f"C{i}"].value
                            thickness_T3 = sheet[f"D{i}"].value
                            thickness = sheet[f"E{i}"].value

                            density = sheet[f"J{i}"].value

                            if sheet.title == "Pente":
                                thickness_Milieu = None
                                thickness_T3 = sheet[f"C{i}"].value
                                thickness = sheet[f"D{i}"].value
                                density = sheet[f"H{i}"].value
                            elif sheet.title == "HD 4x3 (2)":
                                thickness_Milieu = sheet[f"C{i}"].value
                                thickness_T3 = sheet[f"D{i}"].value
                                thickness = sheet[f"E{i}"].value
                                density = sheet[f"N{i}"].value   
                            
                            if hour is not None:
                                facer = 1
                                if hour_str:
                                    try:
                                        current_hour = parse_time_flexibly(hour_str)
                                        if previous_hour and previous_hour > current_hour:
                                            flag = True
                                            roll_over += 1
                                        previous_hour = current_hour

                                        adjusted_datetime = datetime.combine(current_date.date(), current_hour)
                                        offset_minutes = PRODUCT_TIME_OFFSET.get(product_code, default_time)
                                        adjusted_datetime -= timedelta(minutes=offset_minutes)

                                    except ValueError:
                                        continue  # Invalid time, skip row

                            elif thickness_T1 and thickness_T3 is not None and density is not None:
                                facer = 0

                            else:
                                continue

                            if adjusted_datetime is None:
                                print(f"Skipping row in file {file} due to invalid or missing time at line {i}")
                                continue

                            # Call DB lookup
                            timestamp_db, density_db, t1_db, t3_db, total_thickness, _ = lookup_from_db_load(
                                db_loaded,
                                product_code,
                                adjusted_datetime,
                                is_pente
                            )

                            if not timestamp_db and not flag:
                                current_date -= timedelta(days=1)
                                adjusted_datetime -= timedelta(days=1)
                                roll_under += 1
                                # Call DB lookup
                                timestamp_db, density_db, t1_db, t3_db, total_thickness, _ = lookup_from_db_load(
                                    db_loaded,
                                    product_code,
                                    adjusted_datetime,
                                    is_pente
                                )
                                combined_datetime = datetime.combine(current_date.date(), current_hour)
                                timestamp_str = combined_datetime.strftime("%Y-%m-%d %H:%M:%S")
                                current_date += timedelta(days=1)
                                adjusted_datetime += timedelta(days=1)
                            
                            if timestamp_db and flag:
                                combined_datetime = datetime.combine(current_date.date(), current_hour)
                                timestamp_str = combined_datetime.strftime("%Y-%m-%d %H:%M:%S")
                            if not timestamp_db and flag:
                                combined_datetime = datetime.combine(current_date.date(), current_hour)
                                timestamp_str = combined_datetime.strftime("%Y-%m-%d %H:%M:%S")
                            
                            if timestamp_db:
                                db_found += 1

                            records.append([
                                lot_number,
                                tiret,
                                of_number,
                                product_code,
                                description,
                                t_min,
                                t_max,
                                timestamp_str,
                                test_qc,
                                density,
                                thickness_T1,
                                thickness_Milieu,
                                thickness_T3,
                                thickness,
                                facer,
                                pente,
                                timestamp_db,
                                density_db,
                                t1_db,
                                t3_db,
                                total_thickness
                            ])

                            count_lines += 1
                    except Exception as fe:
                        print(f"Failed to read {file_path}: {fe}")
                    count_files += 1

        if records:
            output_dir = os.path.dirname(folder_path.rstrip("/\\"))
            output_csv = os.path.join(output_dir, output_filename)
            df = pd.DataFrame(records, columns=[
                "LotNumber", "tiret", "OF", "Product_code", "Description", "Tmin", "Tmax", "TimeStamp",
                "TestQC", "Density", "Thickness_T1", "Thickness_Milieu", "Thickness_T3", "Thickness",
                "Facer", "Pente", "TimeStamp_DB", "Density_DB", "Thickness_T1_DB", "Thickness_T3_DB", "TotalThickness"
            ])
            df.to_csv(output_csv, index=False)
            print(f"Autocontrole data saved as: {output_csv}")
            print(f"{count_files} files processed, {count_lines} lines written, {lines_in_file} lines read, {db_found} database hits, {same_date} same date, {roll_over} roll over and {roll_under} roll under")
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

def fall_back_sheet(wb, product_code, names):
    i = 0
    while(product_code == "" or product_code == None):
        sheet = wb[names[i]]
        product_code = sheet["G5"].value
        i += 1
    return product_code