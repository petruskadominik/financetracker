import streamlit as st
import pandas as pd
from import_csv import live_import_csv
from db_connect import get_db_connection
from queries import *
from processing import process_transactions
from options import options
import matplotlib.pyplot as plt
import plotly.express as px
import os
import json





def dashboard(cnx, cursor):
    if not (cnx and cursor):
        print("No database connection!")
        return
    st.set_page_config(layout="wide")
    
    
    st.markdown("<h1 style='text-align: center'>Finance tracker</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        pass
    with col2:
        pass
    with col3:
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
    st.markdown("<h2 style='text-align: center'>Monthly summary</h2>", unsafe_allow_html=True)
    monthly1, monthly2, monthly3 = st.columns(3)
    names = ["Bucket"] + months
    monthly_txn.columns = names 
    
    selected_month_data = monthly_txn[['Bucket', selected_month]]
    with monthly3:
        print(selected_month_data.describe())
        selected_month_data[selected_month] = selected_month_data[selected_month].abs()
        st.dataframe(selected_month_data)

    chart_data = selected_month_data[selected_month_data.iloc[:, 1] != 0].copy()
    chart_data.iloc[:, 1] = chart_data.iloc[:, 1].abs()

    # Using plotly for more customization
    

    fig = px.pie(
        chart_data, 
        values=chart_data.columns[1],  # The column with values
        names='Bucket',  # The column with categories
        #title=f'Expenses for {selected_month}'
    )
    fig.update_traces(hovertemplate="%{label}<br>%{value:.2f} €<extra></extra>")
    with monthly2:
        st.plotly_chart(fig)
    # Line chart of bucketed with total
    
    data = fetch_all_transactions(cnx, cursor)
    df = pd.DataFrame(data)
    df.columns = ["id", "Date", "Description", "Amount", "Fee", "Currency", "Bucket", "Subcat"]
    df = df.sort_values(by="Date", ascending=False)
    with monthly1:
        # Exclude 'id' column from display but keep it in df
        # Exclude 'id' column from display but keep it in df for tracking
        display_df = df.drop(columns=["id"])

        edited_df = st.data_editor(
            display_df,
            num_rows="dynamic",
            disabled=["Date", "Description", "Amount", "Fee", "Currency"],
            key="data_editor",
        )

        if not edited_df.equals(display_df):
            if st.button("Save Changes"):
                try:
                    conn, cursor = get_db_connection()
                    if conn and cursor:
                        # Restore 'id' column to align with the original DataFrame
                        edited_df = edited_df.copy()  # Make a copy to avoid modifying Streamlit's state
                        edited_df["id"] = df["id"]

                        # Reorder columns to match the original DataFrame
                        edited_df = edited_df.reindex(columns=df.columns)

                        # Find which rows are different
                        diff_mask = (edited_df != df).any(axis=1)
                        changed_rows = edited_df.loc[diff_mask]
                        
                        if not changed_rows.empty:
                            for index, changed_row in changed_rows.iterrows():
                                row_id = int(df.loc[index, "id"])  # Get ID from original df
                                original_row = df.loc[index]
                                
                                # Create SET clause for only modified columns
                                changed_columns = {
                                    col: changed_row[col] for col in edited_df.columns
                                    if col != "id" and changed_row[col] != original_row[col]
                                }
                                
                                if changed_columns:
                                    set_clause = ", ".join([f"{col} = %s" for col in changed_columns.keys()])
                                    query = f"UPDATE processed_transactions SET {set_clause} WHERE id = %s"
                                    
                                    values = tuple(changed_columns.values()) + (row_id,)
                                    
                                    cursor.execute(query, values)
                                    conn.commit()
                            
                            st.success("Changes saved successfully!")
                except Exception as e:
                    st.error(f"Error saving changes: {e}")

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
            process_transactions(cnx, cursor)
            st.success("Bucket/subcat added successfully!")


    
    bucketed, months = fetch_all_transactions_buckets_with_total(cnx, cursor)
    df = pd.DataFrame(bucketed)
    st.write("Bucketed Transactions per month")
    names = ["Bucket"] + months
    df.columns = names
    df.iloc[:, 1:] = df.iloc[:, 1:].abs()
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

    # Stacked bar chart
    data = fetch_all_transactions(cnx, cursor)
    df = pd.DataFrame(data)
    df.columns = ["id", "Date", "Description", "Amount", "Fee", "Currency", "Bucket", "Subcat"]
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