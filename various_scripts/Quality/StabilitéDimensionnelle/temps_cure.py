import openpyxl
from openpyxl import Workbook
import csv

def filter_column_c_and_return_cd(file_path, match_string):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active

    result = []

    for row in ws.iter_rows(min_row=2, min_col=3, max_col=4):  # C=3, D=4
        c_value = row[0].value
        d_value = row[1].value

        if c_value in match_string:
            result.append((c_value, d_value))

    return result

def load_liberation_data(excel_path):
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb.active
    data = {}
    for row in range(1, sheet.max_row + 1):
        of_value = sheet[f"C{row}"].value
        if of_value is not None:
            of_number = str(of_value).strip()
            data[of_number] = (
                sheet[f"A{row}"].value,
                sheet[f"B{row}"].value,
                sheet[f"E{row}"].value,
                sheet[f"F{row}"].value,
                sheet[f"G{row}"].value,
                sheet[f"I{row}"].value,
                sheet[f"J{row}"].value,
                sheet[f"V{row}"].value
            )
    return data

from datetime import datetime

def joint_data(filtered_data, liberation_data, provided_time_str):
    combined_data = []

    for ci, di in filtered_data:
        key = str(di).strip()
        if key in liberation_data:
            (
                a_val, b_val, e_val, f_val,
                g_val, i_date, j_time, v_date
            ) = liberation_data[key]

            if not i_date or not j_time or not v_date:
                # Skip rows with missing critical date/time info
                print(f"Skipping {key} due to missing date/time data.")
                continue

            # Format timestamp initial
            date_part_initial = i_date.date() if isinstance(i_date, datetime) else datetime.strptime(str(i_date), "%Y-%m-%d").date()
            try:
                time_part_initial = parse_time_string(str(j_time))
            except ValueError:
                print(f"Skipping {key}: invalid j_time format: {j_time}")
                continue

            timeStampInitial = datetime.combine(date_part_initial, time_part_initial)


            # Format timestamp final
            date_part_final = v_date.date() if isinstance(v_date, datetime) else datetime.strptime(str(v_date), "%Y-%m-%d").date()
            time_part_final = datetime.strptime(provided_time_str, "%H:%M:%S").time()

            timeStampFinal = datetime.combine(date_part_final, time_part_final)

            # Compute time difference in hours
            hours_difference = (timeStampFinal - timeStampInitial).total_seconds() / 3600

            # Store all data in a row
            combined_data.append({
                "NatureDefaut": ci,
                "OF": di,
                "Lot": a_val,
                "Tiret": b_val,
                "Descripttion": e_val,
                "minE": f_val,
                "maxE": g_val,
                "dateFab": i_date,
                "timeFab": j_time,
                "dateLib": v_date,
                "timeStampInitial": timeStampInitial.strftime("%Y-%m-%d %H:%M"),
                "timeStampFinal": timeStampFinal.strftime("%Y-%m-%d %H:%M"),
                "hours_difference": round(hours_difference, 2)
            })

    return combined_data

def export_joint_data(excel_filename, csv_filename, *data_sets):
    combined_data = []
    
    # Combine all data lists into one
    for data in data_sets:
        if data:  # skip empty or None
            combined_data.extend(data)

    if not combined_data:
        print("No data to export.")
        return

    # Get all headers (from keys of first entry)
    headers = list(combined_data[0].keys())

    # --- Save to Excel ---
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in combined_data:
        ws.append([row.get(h, "") for h in headers])
    wb.save(excel_filename)
    print(f"Excel file saved as: {excel_filename}")

    # --- Save to CSV ---
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in combined_data:
            writer.writerow(row)
    print(f"CSV file saved as: {csv_filename}")

def parse_time_string(time_str):
    for fmt in ("%H:%M:%S", "%I:%M:%S %p"):
        try:
            return datetime.strptime(time_str, fmt).time()
        except ValueError:
            continue
    raise ValueError(f"Unknown time format: {time_str}")

if __name__ == "__main__":
    liste_path = "./liste1.xlsx"
    match_string = ["Stabilité dimensionnelle (7jrs)", "Stabilité dimensionnelle (edge collapse)",
                    "Stabilité dimensionnelle (edge collapse + taux déformation)",
                    "Stabilité dimensionnelle (taux déformation)", "Stabilité dimensionnelle"]
    liberation_path_2024 = "./Libération OF 2024.xlsx"
    liberation_path_2025 = "./0-Libération OF 2025.xlsx"
    filtered = filter_column_c_and_return_cd(liste_path, match_string)
    liberation_data_2024 = load_liberation_data(liberation_path_2024)
    liberation_data_2025 = load_liberation_data(liberation_path_2025)
    PROVIDED_TIME = "18:00:00"
    data_2024 = joint_data(filtered, liberation_data_2024, PROVIDED_TIME)
    data_2025 = joint_data(filtered, liberation_data_2025, PROVIDED_TIME)
    export_joint_data("stabilite.xlsx", "stabilite.csv", data_2024, data_2025)

def export_joint_data_only_one(data, excel_filename, csv_filename):
    if not data:
        print("No data to export.")
        return

    # Extract column headers from keys of the first dictionary
    headers = list(data[0].keys())

    # --- Save to Excel ---
    wb = Workbook()
    ws = wb.active
    ws.append(headers)  # write header
    for row in data:
        ws.append([row.get(h, "") for h in headers])
    wb.save(excel_filename)
    print(f"Excel file saved as: {excel_filename}")

    # --- Save to CSV ---
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"CSV file saved as: {csv_filename}")

