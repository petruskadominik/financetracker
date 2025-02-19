from db_connect import get_db_connection
import pandas as pd
from rules import rules 

def process_transactions(cnx=None, cursor=None):
    if not (cnx and cursor):
        print("No database connection!")
        return
    cursor.execute("USE financetracker")
    cursor.execute("""
        SELECT id, description, amount FROM Processed_transactions WHERE BUCKET is NULL        
    """,)

    rows = cursor.fetchall()
    print(rows[1])
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




def main():
    cnx, cursor = get_db_connection()
    cursor.execute("USE financetracker")
    if cnx and cursor:
        try:
            process_transactions(cnx=cnx, cursor=cursor)
        finally:
            cursor.close()
            cnx.close()
            print("Connection closed")

if __name__ == "__main__":
    main()