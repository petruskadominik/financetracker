import streamlit as st
import pandas as pd
from import_csv import live_import_csv
from db_connect import get_db_connection
from queries import *
from processing import process_transactions
from rules import *
import matplotlib.pyplot as plt
import plotly.express as px
import os
import json





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

    # Monthly summary

    bucketed, months = fetch_all_transactions_buckets(cnx, cursor)
    monthly_txn = pd.DataFrame(bucketed)
    selected_month = st.selectbox(
    'Select Month',
    months,
    index=len(months)-1
)   
    st.write(selected_month)
    names = ["Bucket"] + months
    monthly_txn.columns = names 
    #Pie chart
    st.write("piechart")
    
    selected_month_data = monthly_txn[['Bucket', selected_month]]
    st.dataframe(selected_month_data)

    chart_data = selected_month_data[selected_month_data.iloc[:, 1] != 0].copy()
    chart_data.iloc[:, 1] = chart_data.iloc[:, 1].abs()

    # Using plotly for more customization
    import plotly.express as px

    fig = px.pie(
        chart_data, 
        values=chart_data.columns[1],  # The column with values
        names='Bucket',  # The column with categories
        #title=f'Expenses for {selected_month}'
    )
    fig.update_traces(hovertemplate="%{label}<br>%{value:.2f} €<extra></extra>")
    st.plotly_chart(fig)
    # Line chart of bucketed with total
    
    data = fetch_all_transactions(cnx, cursor)
    df = pd.DataFrame(data)
    df.columns = ["Date", "Description", "Amount", "Fee", "Currency", "Bucket", "Subcat"]
    df = df.sort_values(by="Date", ascending=False)
    st.write("Recent Transactions")
    st.dataframe(df)
    
    bucketed, months = fetch_all_transactions_buckets_with_total(cnx, cursor)
    df = pd.DataFrame(bucketed)
    st.write("Bucketed Transactions")
    names = ["Bucket"] + months
    df.columns = names
    st.dataframe(df)
    long_df = df.melt(id_vars=["Bucket"], var_name="month", value_name="amount")
    long_df['amount'] = long_df['amount'].abs()
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

    fig = px.line(long_df, x='month', y='amount',color='Bucket')
    st.plotly_chart(fig)

    
    uncategorized = pd.DataFrame(fetch_uncategorised_txn(cnx, cursor))
    if not uncategorized.empty:
        st.subheader('Uncategorized transactions')
        st.dataframe(uncategorized)
    

        # Path to the rules.json file
        RULES_FILE = "rules.json"
        rules = load_rules(RULES_FILE)
        
        # Initialize session state variables if they don't exist
        if "selected_category" not in st.session_state:
            st.session_state.selected_category = list(options.keys())[0]  # Default to first category
        if "selected_value" not in st.session_state:
            st.session_state.selected_value = options[st.session_state.selected_category][0]
        if "text_input" not in st.session_state:
            st.session_state.text_input = ""

        # Function to update second dropdown when category changes
        def update_values():
            st.session_state.selected_value = options[st.session_state.selected_category][0]

        # Text input (used as dictionary key)
        text_input = st.text_input("Enter a name (Key):", st.session_state.text_input)

        # First dropdown (select category)
        category_index = list(options.keys()).index(st.session_state.selected_category)  # Get the index of selected category
        selected_category = st.selectbox(
            "Choose a category:", 
            list(options.keys()), 
            index=category_index,  # Set default selection based on session state
            key="selected_category",
            on_change=update_values  # When changed, update second dropdown
        )

        # Second dropdown (updates dynamically)
        selected_value = st.selectbox(
            f"Choose a value from {st.session_state.selected_category}:",
            options[st.session_state.selected_category],
            key="selected_value"
        )

        # Submit button
        if st.button("Submit"):
            output_dict = {text_input: [selected_category, selected_value]}
            rules.update(output_dict)
            rules.update(output_dict)
            save_rules(rules, RULES_FILE)
            print(output_dict)
            st.write("Generated Dictionary:", output_dict)
            process_transactions(cnx, cursor)


    # Stacked bar chart
    data = fetch_all_transactions(cnx, cursor)
    df = pd.DataFrame(data)
    df.columns = ["Date", "Description", "Amount", "Fee", "Currency", "Bucket", "Subcat"]
    df = df.sort_values(by="Date", ascending=False)    
    bucketed, months = fetch_all_transactions_buckets(cnx, cursor)
    df = pd.DataFrame(bucketed)
    names = ["Bucket"] + months
    df.columns = names
    long_df = df.melt(id_vars=["Bucket"], var_name="month", value_name="amount")
    long_df['amount'] = long_df['amount'].abs()
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
        
def load_rules(RULES_FILE):
        if os.path.exists(RULES_FILE):
            with open(RULES_FILE, "r") as file:
                return json.load(file)
            return
        
def save_rules(rules, RULES_FILE):
    with open(RULES_FILE, "w") as file:
        json.dump(rules, file, indent=4)
    
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