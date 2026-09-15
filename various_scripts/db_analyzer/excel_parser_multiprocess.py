import signal
from datetime import datetime, timedelta, time
from db_lookup import lookup_from_db_load
from load_db import load_database
from load_liberation import load_liberation_data
import openpyxl
import os
from multiprocessing import Pool, cpu_count
from functools import partial

# globals
LIBERATION_DATA = None
DATABASE_DATA = None

def analyze_extract_one_file(
    file_path,
):
    liberation_data = LIBERATION_DATA
    database_data = DATABASE_DATA
    PRODUCT_TIME_OFFSET = {}
    default_time = 10
    records = []
    try:
        file = os.path.basename(file_path)
        date_str = file[:10]  # YYYY-MM-DD
        of_number = os.path.splitext(file)[0][-5:]  # last 5 digits before extension

        if of_number not in liberation_data:
            print(f"{file}: OF number {of_number} not found in Liberation file.")

        lot_number, tiret, description, t_min, t_max, date, test_qc = liberation_data[of_number]
        date_str1 = date.strftime("%Y-%m-%d")

        # if t_max > 4:
        #     default_time = 20

        flag = False
        if date_str == date_str1:
            flag = True
        # else:
        #     print(f"{file}: OF number {of_number}")

        wb = openpyxl.load_workbook(file_path, data_only=True, read_only=True)

        if "pré-emballage" in wb.sheetnames:
            sheet = wb["pré-emballage"]
        else:
            sheet = wb["Plat"]

        product_code = sheet['G5'].value

        pente = 0
        is_pente = False
        if sheet['C13'].value is None:
            pente = 1
            is_pente = True
            if "pré-emballage" in wb.sheetnames:
                sheet = wb["pré-emballage"]
            else:
                sheet = wb["Pente"]
                product_code = sheet['F5'].value
        #else: continue  # TO ONLY HAVE PENTES IN MY FILES
        if not product_code:
            product_code = fall_back_sheet(
                wb, product_code, ["SL", "HD 4x3 (2)", "Emball ISO"]
            )
        if not product_code:
            print(
                f"[WARN] No product code found in {os.path.basename(file_path)} "
                f"(sheets: {wb.sheetnames})"
            )
            return []

        previous_hour = None
        # current_date = datetime.strptime(date_str, "%Y-%m-%d")
        current_date = datetime.strptime(date_str1, "%Y-%m-%d")
        adjusted_datetime = None

        for i in range(13, 76):
            hour = sheet[f"A{i}"].value
            hour_str = ""
            facer = 1

            if hour is not None:
                hour_str = str(hour).strip()
                try:
                    current_hour = parse_time_flexibly(hour_str)
                    if previous_hour and previous_hour > current_hour:
                        flag = True
                    previous_hour = current_hour

                    adjusted_datetime = datetime.combine(current_date.date(), current_hour)
                    offset_minutes = PRODUCT_TIME_OFFSET.get(product_code, default_time)
                    adjusted_datetime -= timedelta(minutes=offset_minutes)

                except ValueError:
                    continue  # Invalid time, skip row
            if adjusted_datetime is None:
                continue

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

            if hour is None and (thickness_T1 and thickness_T3 and density) is not None:
                facer = 0
            if (hour and thickness_T1 and thickness_T3 and density) is None:
                continue

            # Call DB lookup
            timestamp_db, density_db, t1_db, t2_db, t3_db, total_thickness, _ = lookup_from_db_load(
                database_data,
                product_code,
                adjusted_datetime,
                is_pente
            )

            timestamp_str = ""
            if not timestamp_db and not flag:
                current_date -= timedelta(days=1)
                adjusted_datetime -= timedelta(days=1)

                # Call DB lookup
                timestamp_db, density_db, t1_db, t2_db, t3_db, total_thickness, _ = lookup_from_db_load(
                    database_data,
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
                t2_db,
                t3_db,
                total_thickness
            ])

    except Exception as fe:
        print(f"Failed to read {file_path}: {fe}")

    return records

def parse_time_flexibly(time_str):
    parts = time_str.split(":")
    if len(parts) == 2:
        return time(int(parts[0]), int(parts[1]))
    elif len(parts) == 3:
        return time(int(parts[0]), int(parts[1]), int(parts[2]))
    else:
        raise ValueError(f"Unrecognized time format: {time_str}")

def fall_back_sheet(wb, product_code, names):
    for name in names:
        if name not in wb.sheetnames:
            continue
        sheet = wb[name]
        value = sheet["G5"].value
        if value not in (None, ""):
            return value
    return None

def list_excel_files(folder_path):
    files = []
    for root, _, filenames in os.walk(folder_path):
        for f in filenames:
            if f.lower().endswith(('.xlsx', '.xls')) and not f.startswith('~$'):
                files.append(os.path.join(root, f))
    return files

def init_worker(liberation_path, database_path):
    global LIBERATION_DATA, DATABASE_DATA
    LIBERATION_DATA = load_liberation_data(liberation_path)
    DATABASE_DATA  = load_database(database_path)

def analyze_extract_autocontrole(folder_path, liberation_path, database_path):

    excel_files = list_excel_files(folder_path)
    print(f"Found {len(excel_files)} files")
    records = []

    with Pool(
        processes=min(cpu_count(), 4),
        initializer=init_worker,
        initargs=(liberation_path, database_path)
    ) as pool:
        for result in pool.imap_unordered(analyze_extract_one_file, excel_files):
            records.extend(result)

    print(f"{len(records)} lines written")
    return records
