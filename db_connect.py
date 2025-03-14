from constants import *
import mysql.connector

def get_db_connection():
    print("Attempting to connect...")
    try:
        cnx = mysql.connector.connect(user=DB_USER, 
                                    password=DB_PASSWORD,
                                    host=DB_HOST,
                                    port=DB_PORT,
                                    database="financetracker")
        print("Connected successfully!")
        cursor = cnx.cursor()
        return cnx, cursor 
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None, None