import streamlit as st
import pandas as pd
from import_csv import live_import_csv
from db_connect import get_db_connection
from queries import *
from processing import process_transactions
import matplotlib.pyplot as plt
import plotly.express as px


def dashboard(cnx, cursor):
    if not (cnx and cursor):
        print("No database connection!")
        return
    st.set_page_config(layout="wide")
    st.title('Finance tracker')
    
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        live_import_csv(uploaded_file, cnx, cursor)
        process_transactions(cnx, cursor)


    # Automatically read the CSV into a DataFrame
    
    data = fetch_all_transactions(cnx, cursor)
    df = pd.DataFrame(data)
    df.columns = ["Date", "Description", "Amount", "Currency", "Fee", "Bucket", "Subcat"]
    df = df.sort_values(by="Date", ascending=False)
    st.write("Recent Transactions")
    st.dataframe(df)
    st.subheader('Spending by Bucket')
    
    
    by_month = fetch_total_by_month(cnx, cursor)
    for row in by_month:
        month, total, count = row
        print(f"Month: {month}, Total Amount: {total}, Transactions: {count}")

    df = pd.DataFrame(by_month)
    df.columns = ["Date", "Total", "Transaction count"]
    st.dataframe(df)

    bucketed, months = fetch_all_transactions_buckets(cnx, cursor)
    df = pd.DataFrame(bucketed)
    st.write("Bucketed Transactions")
    names = ["Bucket"] + months
    df.columns = names
    st.dataframe(df)
    long_df = df.melt(id_vars=["Bucket"], var_name="month", value_name="amount")
    long_df['amount'] = long_df['amount'].abs()
    st.dataframe(long_df)
    print(long_df.keys())

    # Create the stacked bar chart using Plotly Express
    fig = px.bar(
        long_df,                   # DataFrame in long format
        x="month",                 # X-axis: Months
        y="amount",                # Y-axis: Amount spent
        color="Bucket",            # Stacked by bucket/category
        title="Spending by Month and Category (Stacked)",
        labels={"amount": "Amount ($)", "month": "Month", "bucket": "Category"}
    )

    # Display the chart in Streamlit
    st.plotly_chart(fig)

    #stacked line chart
    fig = px.area(long_df, x='month', y='amount', line_group='Bucket', color='Bucket')
    st.plotly_chart(fig)

    fig = px.line(long_df, x='month', y='amount',color='Bucket')
    st.plotly_chart(fig)

    
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