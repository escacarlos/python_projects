import openpyxl
import pandas as pd
from collections import defaultdict

def read_selected_columns(file_path):
    wb = openpyxl.load_workbook(file_path, data_only=True)
    ws = wb.active

    data = []

    for row in ws.iter_rows(min_row=3, min_col=3, max_col=22):
        row_data = {
            'C': row[0].value,   # Column C (index 0 since min_col=3)
            'R': row[15].value,  # Column R
            'S': row[16].value,  # Column S
            'T': row[17].value,  # Column T
            'U': row[18].value,  # Column U
            'V': row[19].value   # Column V
        }
        data.append(row_data)

    return data

def average_grouped_data(data):
    grouped = defaultdict(lambda: {
        'R_sum': 0.0, 'R_count': 0,
        'S_sum': 0.0, 'S_count': 0,
        'T_sum': 0.0, 'T_count': 0,
        'U_sum': 0.0, 'U_count': 0,
        'V_sum': 0.0, 'V_count': 0
    })

    for row in data:
        key = row['C']
        if key is None:
            continue  # Skip rows without a key

        for col in ['R', 'S', 'T', 'U', 'V']:
            value = row[col]
            if isinstance(value, (int, float)):
                grouped[key][f'{col}_sum'] += value
                grouped[key][f'{col}_count'] += 1

    # Compute averages
    result = {}
    for key, stats in grouped.items():
        result[key] = {
            'R_avg': stats['R_sum'] / stats['R_count'] if stats['R_count'] else None,
            'S_avg': stats['S_sum'] / stats['S_count'] if stats['S_count'] else None,
            'T_avg': stats['T_sum'] / stats['T_count'] if stats['T_count'] else None,
            'U_avg': stats['U_sum'] / stats['U_count'] if stats['U_count'] else None,
            'V_avg': stats['V_sum'] / stats['V_count'] if stats['V_count'] else None,
            'R_count': stats['R_count'],
            'S_count': stats['S_count'],
            'T_count': stats['T_count'],
            'U_count': stats['U_count'],
            'V_count': stats['V_count']
        }

    return result

def save_averages_to_files(averaged_data, excel_filename='averages.xlsx', csv_filename='averages.csv'):
    # Convert dictionary to DataFrame
    df = pd.DataFrame.from_dict(averaged_data, orient='index').reset_index()
    df.rename(columns={'index': 'C'}, inplace=True)

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
    data = read_selected_columns("C:\\Users\\cescalantecastillo\\Documents\\ISO+.xlsx")
    averaged = average_grouped_data(data)
    save_averages_to_files(averaged, "grouped_averages.xlsx", "grouped_averages.csv")
    save_raw_data_to_files(data, "raw_data.xlsx", "raw_data.csv")
    for row in data:
        print(row)

    for key, stats in averaged.items():
        print(f"{key}: {stats}")