from db_connect import get_db_connection
import pandas as pd
import os
import json

def process_transactions(cnx=None, cursor=None):
    if not (cnx and cursor):
        print("No database connection!")
        return
    cursor.execute("USE financetracker")
    cursor.execute("""
        SELECT id, description, amount FROM Processed_transactions WHERE BUCKET is NULL        
    """,)
    
    RULES_FILE = "rules.json"
    rules = load_rules(RULES_FILE)

    rows = cursor.fetchall()
    for key in rules: 
        for row in rows:
            if key in row[1]:
                bucket, subcat = rules[key]
                cursor.execute("""
            UPDATE Processed_transactions 
            SET bucket = %s, subcat = %s
            WHERE id = %s        
        """,(bucket, subcat, row[0]))
    cnx.commit()

def load_rules(RULES_FILE):
        if os.path.exists(RULES_FILE):
            with open(RULES_FILE, "r") as file:
                return json.load(file)
            return


def main():
    cnx, cursor = get_db_connection()
    if cnx and cursor:
        try:
            cursor.execute("USE financetracker")
            process_transactions(cnx=cnx, cursor=cursor)
        finally:
            cursor.close()
            cnx.close()
            print("Connection closed")

if __name__ == "__main__":
    main()