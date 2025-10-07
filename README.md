\# 🏦 Bank Statement Analyzer



A simple Python toolkit that helps you transform your bank’s CSV statement into a structured JSON file and generate detailed transaction analytics — all with one command.



\## 🚀 Features

\- Converts raw CSV bank statements into clean JSON

\- Calculates total debits (money spent) and credits (money received)

\- Finds top debit and credit transactions

\- Computes monthly summaries (e.g., August 2025)

\- Shows the net balance difference (credits - debits)



\## 🧰 Usage

```bash

\# Step 1: Convert CSV → JSON

python create\_json\_from\_csv.py "2024\_Statement.csv"



\# Step 2: Generate analytics from JSON

python get\_details\_from\_json.py "2024\_Statement.json" \[optional: month-year]



\# Or run both steps with:

run\_for\_details.bat "2024\_Statement.csv"



