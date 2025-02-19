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
4. Run setup.py (This will connect to your DBServer create nessesary Database and tables if not created already)
5. Import your statements to ~/statements
6. Run import.py (This will import all statements from ~/statements ignoring duplicate transactions)


## Current Features
1. Communication with MySQL server
2. Creating DB and tables required for Financetracker
3. Importing Revolut bank statement in CSV format

## WIP Features
1. Categorisation of transactions
2. GUI display of data
