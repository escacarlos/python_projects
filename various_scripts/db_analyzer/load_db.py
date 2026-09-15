import pandas as pd
import sqlite3
from time import perf_counter

def load_database(database_path):
    conn = sqlite3.connect(database_path)
    query = """
        SELECT 
            req.ProductCode,
            req.Timestamp,
            res.InsulatorDensity,
            res.TotalThickness,
            res.ThicknessSamples
        FROM Requests req
        JOIN Results res ON res.RequestId = req.RequestId
        WHERE res.InsulatorDensity IS NOT NULL
    """
    df = pd.read_sql_query(query, conn, parse_dates=["Timestamp"])
    conn.close()

    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    return df

if __name__ == "__main__":
    database_path = "C:/Users/escac/source/db_data/DensityMeasurement_old.db"
    start = perf_counter()
    db = load_database(database_path)
    print(f"time taken: {perf_counter() - start} seconds")