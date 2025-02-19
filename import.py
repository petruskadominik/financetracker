import mysql.connector
import pandas as pd
import os
import numpy as np
from constants import *

def get_db_connection():
    print("Attempting to connect...")
    try:
        cnx = mysql.connector.connect(user=DB_USER, 
                                    password=DB_PASSWORD,
                                    host=DB_HOST,
                                    port=DB_PORT)
        print("Connected successfully!")
        cursor = cnx.cursor()
        cursor.execute("USE financetracker")
        return cnx, cursor
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None

def import_revolut_statements(folder_path="statements", cnx=None, cursor=None):
    if not (cnx and cursor):
        print("No database connection!")
        return
    
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    print(csv_files[0])
    for file in csv_files:
        path = os.path.join(folder_path, file)
        df = pd.read_csv(path)
        df = df.replace({np.nan: None})
        print(df.head())
        for _, row in df.iterrows():
            cursor.execute("""
        INSERT IGNORE INTO raw_transactions_revolut 
        (type, product, started_date, completed_date, description, 
         amount, fee, currency, state, balance)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, tuple(row))
    cnx.commit()

    cursor.execute("""
        SELECT started_date, completed_date, description, amount, fee, currency
                   FROM raw_transactions_revolut 
            WHERE STATE != "REVERTED"        
    """,)

    rows = cursor.fetchall()
    for row in rows:
        cursor.execute("""
        INSERT IGNORE INTO Processed_transactions 
                       (started_date, completed_date, description, 
         amount, fee, currency) VALUES (%s, %s, %s, %s, %s, %s)
        """, row)
    cnx.commit()
    
    if not csv_files:
        print("No CSV files found in statements folder")
        return

def main():
    cnx, cursor = get_db_connection()
    if cnx and cursor:
        try:
            import_revolut_statements(cnx=cnx, cursor=cursor)
        finally:
            cursor.close()
            cnx.close()
            print("Connection closed")

if __name__ == "__main__":
    main()