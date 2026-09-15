from excel_parser import analyze_extract_autocontrole
from time import perf_counter
import pandas as pd
import os
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl.worksheet._reader")

def prepare_results(
    autocontrole_path,
    liberation_path,
    database_path,
    output_filename
):
    records = analyze_extract_autocontrole(autocontrole_path, liberation_path, database_path)

    if records:
        output_dir = os.path.dirname(autocontrole_path.rstrip("/\\"))
        output_csv = os.path.join(output_dir, output_filename)
        df = pd.DataFrame(records, columns=[
            "LotNumber", "tiret", "OF", "Product_code", "Description", "Tmin", "Tmax", "TimeStamp",
            "TestQC", "Density", "Thickness_T1", "Thickness_Milieu", "Thickness_T3", "Thickness",
            "Facer", "Pente", "TimeStamp_DB", "Density_DB", "Thickness_T1_DB", "Thickness_T2_DB",
            "Thickness_T3_DB", "TotalThickness"
        ])
        df.to_csv(output_csv, index=False)
        print(f"Autocontrole data saved as: {output_csv}")

    else:
        print("No valid data found in the provided folder.")

if __name__ == "__main__":
    liberation_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\0-Libération OF 2025.xlsx"
    
    autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_1"
    database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement_old.db"
    start = perf_counter()
    prepare_results(autocontrole_path, liberation_path, database_path, "file1p.csv")
    print(f"time taken: {perf_counter() - start} seconds")

    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_2"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement4.db"
    # start = perf_counter()
    # prepare_results(autocontrole_path, liberation_path, database_path, "file2p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")
    #
    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_3"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement6.db"
    # start = perf_counter()
    # prepare_results(autocontrole_path, liberation_path, database_path, "file3p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")
    #
    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_4"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement6.db"
    # start = perf_counter()
    # prepare_results(autocontrole_path, liberation_path, database_path, "file4p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")
    #
    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_5"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement7.db"
    # start = perf_counter()
    # prepare_results(autocontrole_path, liberation_path, database_path, "file5p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")
    #
    # autocontrole_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\Autocontrole\\Autocontrole_6"
    # database_path = "C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement8.db"
    # start = perf_counter()
    # prepare_results(autocontrole_path, liberation_path, database_path, "file6p.csv")
    # print(f"time taken: {perf_counter() - start} seconds")

