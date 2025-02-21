from datetime import datetime
import pandas as pd

def fetch_all_transactions(cnx, cursor):
    cursor.execute("USE financetracker")
    if not (cnx and cursor):
            print("No database connection!")
            return
    cursor.execute("""
        SELECT started_date, description, amount, fee, currency, bucket, subcat
                   FROM Processed_transactions        
    """,)
    data = cursor.fetchall()
    return data

def fetch_total_by_month(cnx, cursor):
    cursor.execute("USE financetracker")
    if not (cnx and cursor):
            print("No database connection!")
            return
    cursor.execute("""
        SELECT DATE_FORMAT(started_date, '%Y-%m') AS month_group,
       SUM(amount) AS total_amount,
       COUNT(*) AS transaction_count
FROM Processed_transactions
WHERE bucket not in ('Domino', 'Maggie')
GROUP BY month_group
ORDER BY month_group desc       
    """,)
    data = cursor.fetchall()
    return data

def fetch_all_transactions_buckets(cnx, cursor):
    
    if not (cnx and cursor):
            print("No database connection!")
            return
    cursor.execute("USE financetracker")
    cursor.execute("SELECT MIN(started_date) FROM processed_transactions WHERE started_date IS NOT NULL")
    oldest_date = cursor.fetchone()[0]

    if not oldest_date:
        print("No transactions found.")
        cursor.close()
        conn.close()
        exit()

    current_date = datetime.now()
    months = []
    temp_date = datetime(oldest_date.year, oldest_date.month, 1)

    while temp_date <= current_date:
        months.append(temp_date.strftime('%Y-%m'))
        if temp_date.month == 12:
            temp_date = datetime(temp_date.year + 1, 1, 1)
        else:
            temp_date = datetime(temp_date.year, temp_date.month + 1, 1)

    columns = [f"SUM(CASE WHEN DATE_FORMAT(started_date, '%Y-%m') = '{month}' THEN amount ELSE 0 END) AS `{month}`" for month in months]

    query = f"""
        SELECT bucket, {", ".join(columns)}
        FROM processed_transactions
        where bucket not in ( 'Domino', 'Maggie')
        GROUP BY bucket
        ORDER BY bucket;
    """

    # Step 4: Execute query
    cursor.execute(query)
    results = cursor.fetchall()
    
    df = pd.DataFrame(results, columns=["bucket"] + months)
    df.set_index("bucket", inplace=True)  

    return results, months


def fetch_uncategorised_txn(cnx, cursor):
    if not (cnx and cursor):
        print("No database connection!")
        return
            
     
    cursor.execute("""USE financetracker""")
    cursor.execute("""
                   SELECT * FROM processed_transactions
                   WHERE bucket is null and subcat is null""")
    
    data = cursor.fetchall()
    return data