from time import perf_counter
from load_db import load_database
from load_liberation import load_liberation_data

if __name__ == "__main__":
    start = perf_counter()
    db_loaded = load_database("C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\DensityMeasurement6.db")
    finish_db = perf_counter()
    liberation_data = load_liberation_data("C:\\Users\\cescalantecastillo\\Documents\\DATABASE_AGMANIC\\0-Libération OF 2025.xlsx")
    finish_ld = perf_counter()
    print(f"time taken loading database: {finish_db - start} seconds")
    print(f"time taken loading liberation file: {finish_ld - start} seconds")
