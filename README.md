# 🏦 Bank Statement Analyzer



A simple Python toolkit that helps you transform your bank’s CSV statement into a structured JSON file and generate detailed transaction analytics — all with one command.



## 🚀 Features

\- Converts raw CSV bank statements into clean JSON

\- Calculates total debits (money spent) and credits (money received)

\- Finds top debit and credit transactions

\- Computes monthly summaries (e.g., August 2025)

\- Shows the net balance difference (credits - debits)



## 🧰 Usage

```bash

# Step 1: Convert CSV → JSON

python create_json_from_csv.py "2024_Statement.csv"



# Step 2: Generate analytics from JSON

python get_details_from_json.py "2024_Statement.json" [optional: month-year]



# Or run both steps with:

run_for_details.bat "2024_Statement.csv" [optional: month-year]



