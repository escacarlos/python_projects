import openpyxl

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
                sheet[f"N{row}"].value
            )
    return data