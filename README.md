# Financial Tracker

This is a basic Financial tracker that will take your bank statement, import it into MySQL database, categorise transactions, and show you what you are spending money on.
This is a personal project, so it will be tailored to me, and rules for categorization will be tailored to my spending so rules for that might need to be edited and added if you want to get any use from this,
also categories are made to fit my needs.
Currently only supports CSV statements from Revolut Bank

## Prerequisites 
1. MySQL server 8.3 (only tested with this version, might work with other but i don't know)
2. Python 3.10.12 (only tested with this version, might work with other but i don't know)
3. Install Python pip if not already installed:
   ```bash
   sudo apt install python3-pip
   pip install -r requirements.txt```

## Setup
1. Clone the repository
2. Copy `constants_template.py` to `constants.py`
3. Update database credentials in `constants.py`
4. Run ./main.sh (this will connect to databease create tables, and creates streamlit dashboard available at http://localhost:8501)


## Current Features
1. Communication with MySQL server
2. Creating DB and tables required for Financetracker
3. Importing Revolut bank statement in CSV format via webui
4. Transaction filtering
5. Display data on dashboard, edit DB entries on dashboard

## Ideas for future
1. Add more csv format support(probably just banks i use)
2. Add profiles that would have acess to different tables(so that i could deferentiate between my and shared finanes)
