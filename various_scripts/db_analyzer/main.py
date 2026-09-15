from excel_parser import analyze_extract
from time import perf_counter
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.worksheet._reader")

if __name__ == "__main__":
    liberation_path = "C:/Users/escac/source/db_data/0-Libération OF 2025.xlsx"
    
    autocontrole_path = "C:/Users/escac/source/db_data/Autocontrole_first"
    database_path = "C:/Users/escac/source/db_data/DensityMeasurement_old.db"
    start = perf_counter()
    analyze_extract(autocontrole_path, liberation_path, database_path, True, "file1p.csv")
    print(f"time taken: {perf_counter() - start} seconds")

    # autocontrole_path = "C:/Users/escac/source/db_data/Autocontrole_second"
    # database_path = "C:/Users/escac/source/db_data/DensityMeasurement4.db"
    # start = perf_counter()
    # analyze_extract(autocontrole_path, liberation_path, database_path, True, "file2p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")

    # autocontrole_path = "C:/Users/escac/source/db_data/Autocontrole_third"
    # database_path = "C:/Users/escac/source/db_data/DensityMeasurement6.db"
    # start = perf_counter()
    # analyze_extract(autocontrole_path, liberation_path, database_path, True, "file3p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")

    # autocontrole_path = "C:/Users/escac/source/db_data/Autocontrole_fourth"
    # database_path = "C:/Users/escac/source/db_data/DensityMeasurement6.db"
    # start = perf_counter()
    # analyze_extract(autocontrole_path, liberation_path, database_path, False, "file4p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")

