import openpyxl
import pandas as pd
from collections import defaultdict

def read_selected_columns(file_path):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active

    data = []

    for row in ws.iter_rows(min_row=1, min_col=2, max_col=14):
        row_data = {
            'Supplier Name': row[0].value,  # B
            'Thickness': row[11].value,     # M (12th col from B)
            'Weight': row[12].value,        # N (13th col from B)
        }
        data.append(row_data)

    return data

def average_grouped_data(data):
    grouped = defaultdict(lambda: {
        'Thickness_sum': 0.0, 'Thickness_count': 0,
        'Weight_sum': 0.0, 'Weight_count': 0,
    })

    for row in data:
        key = row['Supplier Name']
        if key is None:
            continue  # Skip rows without a key

        for col in ['Thickness', 'Weight']:
            value = row[col]
            if isinstance(value, (int, float)):
                grouped[key][f'{col}_sum'] += value
                grouped[key][f'{col}_count'] += 1

    # Compute averages
    result = {}
    for key, stats in grouped.items():
        result[key] = {
            'Thickness_avg': stats['Thickness_sum'] / stats['Thickness_count'] if stats['Thickness_count'] else None,
            'Weight_avg': stats['Weight_sum'] / stats['Weight_count'] if stats['Weight_count'] else None,
            'Thickness_count': stats['Thickness_count'],
            'Weight_count': stats['Weight_count'],
        }

    return result

def save_averages_to_files(averaged_data, excel_filename='averages.xlsx', csv_filename='averages.csv'):
    # Convert dictionary to DataFrame
    df = pd.DataFrame.from_dict(averaged_data, orient='index').reset_index()
    df.rename(columns={'index': 'Supplier Name'}, inplace=True)

    # Save to Excel
    df.to_excel(excel_filename, index=False)

    # Save to CSV
    df.to_csv(csv_filename, index=False)

    print(f"Saved to '{excel_filename}' and '{csv_filename}'")

def save_raw_data_to_files(data, excel_filename='raw_data.xlsx', csv_filename='raw_data.csv'):
    # Convert list of dicts to a DataFrame
    df = pd.DataFrame(data)

    # Save to Excel
    df.to_excel(excel_filename, index=False)

    # Save to CSV
    df.to_csv(csv_filename, index=False)

    print(f"Raw data saved to '{excel_filename}' and '{csv_filename}'")

if __name__ == '__main__':
    data = read_selected_columns("C:\\Users\\cescalantecastillo\\Documents\\ISO.xlsx")
    averaged = average_grouped_data(data)
    save_averages_to_files(averaged, "grouped_averages.xlsx", "grouped_averages.csv")
    save_raw_data_to_files(data, "raw_data.xlsx", "raw_data.csv")
    for row in data:
        print(row)

    for key, stats in averaged.items():
        print(f"{key}: {stats}")