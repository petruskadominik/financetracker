import mysql.connector
from constants import *

print("Attempting to connect...")
try:
    cnx = mysql.connector.connect(user=DB_USER, 
                                password=DB_PASSWORD,
                                host=DB_HOST,
                                port=DB_PORT)
    print("Connected successfully!")
    
    cursor = cnx.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS financetracker")
    cursor.execute("USE financetracker")
    cursor.execute("SELECT VERSION()")
    version = cursor.fetchone()
    print(f"MySQL version: {version[0]}")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS raw_transactions_revolut (
        id INT AUTO_INCREMENT,
        type VARCHAR(255),
        product VARCHAR(255),
        started_date DATETIME,
        completed_date DATETIME,
        description VARCHAR(255),
        amount DECIMAL(10,2),
        fee DECIMAL(10,2),
        currency CHAR(3),
        state VARCHAR(255),
        balance DECIMAL(10,2),
        PRIMARY KEY (id),
        UNIQUE KEY unique_transaction (started_date, amount, description)
    )""")
    print("Table created successfully!")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processed_transactions (
        id INT AUTO_INCREMENT,
        started_date DATETIME,
        completed_date DATETIME,
        description VARCHAR(255),
        amount DECIMAL(10,2),
        fee DECIMAL(10,2),
        currency CHAR(3),
        bucket VARCHAR(255),
        subcat VARCHAR(255),
        PRIMARY KEY (id),
        UNIQUE KEY unique_transaction (started_date, amount, description)
    )""")
    print("Table created successfully!")


    
except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    if 'cnx' in locals() and cnx.is_connected():
        cursor.close()
        cnx.close()
        print("Connection closed")



        