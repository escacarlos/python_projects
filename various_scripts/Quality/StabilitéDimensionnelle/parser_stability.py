import os
import openpyxl
import pandas as pd
from time import perf_counter
# from __future__ import annotations
from typing import Any, Dict, List, Tuple
from openpyxl.worksheet.worksheet import Worksheet

def load_liberation_data(
    excel_path: str
) -> Dict[str, Tuple[Any, Any, Any, Any, Any]]:
    """
    Loads specific columns (E, F, G, I, N) from an Excel workbook and
    maps them to lot identifiers constructed from columns A and B.

    Args:
        excel_path: the folder_path to the excel file to be processed.
    
    Returns:
        A dictionnary where the key is the lot number
    """
    wb = openpyxl.load_workbook(excel_path, data_only=True)
    sheet = wb.active
    if sheet is None:
        raise ValueError("The workbook has no active sheet.")
    
    data: Dict[str, Tuple[Any, Any, Any, Any, Any]] = {}

    for row in range(1, sheet.max_row + 1):
        lot_number = str(sheet[f"A{row}" or ""].value).strip()
        tiret_raw = str(sheet[f"B{row}"].value)
        lot = ""

        if tiret_raw:
            tiret_part = str(tiret_raw).split('.')[0].split(',')[0]
            lot = f"{lot_number}-{tiret_part.strip()}"

        if lot:
            data[lot] = (
                # sheet[f"C{row}"].value,
                sheet[f"E{row}"].value,
                sheet[f"F{row}"].value,
                sheet[f"G{row}"].value,
                sheet[f"I{row}"].value,
                sheet[f"N{row}"].value
            )
    return data

def parser_stability(
    folder_path: str, 
    liberation_path: str
) -> list[List[Any]]:
    """
    Parses stability Excel files in a folder and extracts measurement data.

    Args:
        folder_path: Path to the directory containing stability Excel files.
        liberation_path: Path to the liberation Excel file.

    Returns:
        A list of records, where each record is a list containing:
        [lot, description, t_min, t_max, date, test_qc, lar_t1_4h, lar_t3_4h, 
        lar_t1_7j, lar_t3_7j]
    """
    count_files = 0
    count_days = 0
    count_entries = 0
    records: List[List[Any]] = []
    try:
        liberation_data: Dict[str, Tuple[Any, Any, Any, Any, Any]] \
            = load_liberation_data(liberation_path)
        
        for root, _, files in os.walk(folder_path):
            for filename in files:
                if filename.lower().startswith('~$'):
                    continue
                if not filename.lower().endswith(('.xlsx', '.xls')):
                    continue
                
                file_path = os.path.join(root, filename)
                try:

                    workbook = openpyxl.load_workbook(file_path, data_only=True)

                    for sheet_name in workbook.sheetnames:
                        sheet = workbook[sheet_name]
                        if sheet_name.lower() == 'template': 
                            continue

                        if not isinstance(sheet, Worksheet):
                            continue

                        for row in range(6, sheet.max_row):
                            cell_value = sheet[f"D{row}"].value
                            if not isinstance(cell_value, str):
                                continue

                            if cell_value.startswith(("P24","P25")):
                                
                                lot_parts = cell_value.strip() \
                                    .split(',')[0].split('.')
                                
                                lot_id = lot_parts[0].strip()

                                if lot_id not in liberation_data:
                                    continue

                                lar_t1_4h = sheet[f"I{row + 11}"].value
                                lar_t3_4h = sheet[f"S{row + 11}"].value
                                lar_t1_7j = sheet[f"I{row + 12}"].value
                                lar_t3_7j = sheet[f"S{row + 12}"].value

                                description, t_min, t_max, date, test_qc \
                                    = liberation_data[lot_id]
                                
                                records.append([
                                    lot_id, 
                                    description, 
                                    t_min, 
                                    t_max, 
                                    date, 
                                    test_qc, 
                                    lar_t1_4h, 
                                    lar_t3_4h, 
                                    lar_t1_7j, 
                                    lar_t3_7j
                                ])
                                count_entries += 1
                        
                        count_days +=1

                except Exception as e:
                    print(f"Failed to read {file_path}: {e}")
                count_files += 1
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    print(f"{count_files} files processed, \
            {count_days} sheets read, \
            {count_entries} entries written.")
    return records

def write_to_csv(
    folder_path: str, 
    out_file_name: str, 
    records: list[List[Any]]
) -> None:
    """
    Writes the records to a csv file

    Args:
        folder_path, where the csv file is going to be created
        out_file_name, name of the output csv file
    """
    output_dir = os.path.dirname(folder_path.rstrip("/\\"))
    output_csv = os.path.join(output_dir, out_file_name)
    if records:
        df = pd.DataFrame(records, columns=[
            'Lot', 'Description', 'Emin', 'Emax', 'DateFabrication', 'TestQC',
            'Lar_T1_4h','Lar_T3_4h', 'Lar_T1_7j', 'Lar_T3_7j'
        ])
        df.to_csv(output_csv, index=False)
        # print(f"Dimensional Stability saved as: {output_csv}")
        
if __name__ == '__main__':
    stability_path1 = 'C:/Users/cescalantecastillo/Documents/stability2025'
    liberation_path1 = 'C:/Users/cescalantecastillo/Documents \
        /DATABASE_AGMANIC/0-Libération OF 2025.xlsx'
    start = perf_counter()
    records1 = parser_stability(stability_path1, liberation_path1)
    write_to_csv(stability_path1, "info_stability2025.csv", records1)
    print(f"time taken: {perf_counter() - start} seconds")

    stability_path2 = 'C:/Users/cescalantecastillo/Documents/stability2024'
    liberation_path2 = 'C:/Users/cescalantecastillo/Documents \
        /Libération OF 2024.xlsx'
    records2 = parser_stability(stability_path2, liberation_path2)
    write_to_csv(stability_path2, "info_stability2024.csv", records2)
    print(f"time taken: {perf_counter() - start} seconds")
