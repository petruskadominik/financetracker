import streamlit as st
import pandas as pd
from db_connect import get_db_connection

def dashboard(cnx, cursor):
    if not (cnx and cursor):
        print("No database connection!")
        return
    st.title('Finance tracker')
    cursor.execute("USE financetracker")
    cursor.execute("""
        SELECT * FROM Processed_transactions        
    """,)
    data = cursor.fetchall()
    st.sidebar.header('Filters')
    st.write("Recent Transactions")
    st.dataframe(data)
    st.subheader('Spending by Category')


def main():
    cnx, cursor = get_db_connection()
    if cnx and cursor:
        try:
            dashboard(cnx=cnx, cursor=cursor)
        finally:
            cursor.close()
            cnx.close()
            print("Connection closed")

if __name__ == "__main__":
    main()