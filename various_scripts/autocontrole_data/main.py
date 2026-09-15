from excel_parser import analyze_extract
from time import perf_counter
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.worksheet._reader")

if __name__ == "__main__":
    liberation_path = "C:\\Users\\cescalantecastillo\\Documents\\MyDocs\\2026_Agmanic\\0-Libération OF 2025.xlsx"
    
    autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\MyDocs\\2026_Agmanic\\hd"
    start = perf_counter()
    analyze_extract(autocontrole_path, liberation_path, "file2p.csv")
    print(f"time taken: {perf_counter() - start} seconds")

    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_2"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement4.db"
    # start = perf_counter()
    # analyze_extract(autocontrole_path, liberation_path, database_path, True, "file2p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")
    #
    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_3"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement6.db"
    # start = perf_counter()
    # analyze_extract(autocontrole_path, liberation_path, database_path, True, "file3p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")
    #
    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_4"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement6.db"
    # start = perf_counter()
    # analyze_extract(autocontrole_path, liberation_path, database_path, False, "file4p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")
    #
    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_5"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement7.db"
    # start = perf_counter()
    # analyze_extract(autocontrole_path, liberation_path, database_path, False, "file5p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")
    #
    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_6"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement8.db"
    # start = perf_counter()
    # analyze_extract(autocontrole_path, liberation_path, database_path, False, "file6p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")

