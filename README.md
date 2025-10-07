# 💰 Bank Transaction Analyzer (CSV → JSON → Insights + LangGraph Chat)

This project automates the analysis of bank statements by converting CSV files into structured JSON, extracting financial insights (spending, income, monthly totals, top transactions), and enabling interactive chat-based queries using **LangGraph**, **OpenAI’s LLM**, and **Gradio**.

---

## 📂 Project Overview

### Components

| File                            | Purpose                                                                                                                                 |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **`create_json_from_csv.py`**   | Converts raw CSV bank statements into clean JSON files with withdrawal/deposit flags.                                                   |
| **`get_details_from_json.py`**  | Analyzes JSON transactions to compute totals, top transactions, and monthly summaries.                                                  |
| **`lang_graph_code_gradio.py`** | Builds an interactive chat interface using **LangGraph** and **Gradio**, allowing users to query spending patterns in natural language. |
| **`run_for_details.bat`**       | Windows batch script to automate the execution of the JSON extraction and transaction analysis pipeline.                                |

---

## 🧠 Key Features

* ✅ **Automatic Header Detection** – Supports flexible column names like `Tran Date`, `DR`, `CR`, etc.
* ✅ **CSV → JSON Conversion** with intelligent mapping.
* ✅ **Transaction Categorization** – Automatically flags debit/credit transactions.
* ✅ **Summary Metrics**

  * Total debited, credited, and net balance.
  * Monthly totals.
  * Top credit/debit transactions.
* ✅ **LLM-Powered Querying** – Ask questions like:

  * *“How much did I spend on groceries?”*
  * *“Show me transactions related to salary.”*
* ✅ **Gradio Chat UI** with real-time responses.

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your-username>/bank-transaction-analyzer.git
cd bank-transaction-analyzer
```

### 2️⃣ Create and Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate      # on macOS/Linux
venv\Scripts\activate         # on Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

**Example requirements.txt**

```
gradio
langgraph
langchain-openai
python-dotenv
```

### 4️⃣ Set OpenAI API Key

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 🧾 Usage Guide

### 🔹 Step 1: Convert CSV to JSON

```bash
python create_json_from_csv.py "2024_Statement.csv"
```

**Output:**
`2024_Statement.json` – A structured JSON file with parsed transaction records.

---

### 🔹 Step 2: Analyze Transactions

```bash
python get_details_from_json.py "2024_Statement.json"
```

**Example Output:**

```
📄 File: 2024_Statement.json
--------------------------------------------------
Total amount spent (DR): 85,340.00
Total amount received (CR): 1,25,000.00
Net balance (CR - DR): 39,660.00

💸 Max DR Transaction:
  Amount: 15,000.0
  PARTICULARS: CREDIT CARD PAYMENT

💰 Max CR Transaction:
  Amount: 25,000.0
  PARTICULARS: SALARY CREDIT
```

You can also filter by month:

```bash
python get_details_from_json.py "2024_Statement.json" [optional: month-year]
```

---

### 🔹 Step 3: Chat with Your Data

Launch the **interactive analyzer**:

```bash
python lang_graph_code_gradio.py
```

This opens a browser-based chat where you can upload your transaction CSV and ask questions like:

> 💬 *"How much did I spend on Amazon"*

---

### 🔹 Step 4: Automate Everything (Optional)

On Windows, simply double-click:

```
run_for_details.bat "2024_Statement.csv" [optional: month-year]
```

It will convert CSV → JSON → summarize details automatically.

---

## 🧩 Project Architecture

```text
+-------------------------+
|  Bank CSV Statement     |
+------------+------------+
             |
             v
+-------------------------+
| create_json_from_csv.py |
| → Parse headers & data  |
| → Add withdrawal flag   |
+------------+------------+
             |
             v
+-------------------------+
| get_details_from_json.py|
| → Compute totals, max,  |
|   top transactions, etc |
+------------+------------+
             |
             v
+-------------------------+
| lang_graph_code_gradio  |
| → LLM-powered Q&A UI    |
| → Natural language chat |
+-------------------------+
```

---

## 🧠 Example Queries in Gradio Chat

| Query                            | Example Response                              |
| -------------------------------- | --------------------------------------------- |
| “How much did I spend on rent”   | 💸 You spent ₹x on rent.                     |
| “How much did I spend on Amazon” | 💸 You spent ₹y on amazon.                   |

---

## 🪄 Tech Stack

* **Python 3.9+**
* **LangGraph** – for defining reasoning pipelines.
* **LangChain + OpenAI GPT-4o-mini** – for natural language interpretation.
* **Gradio** – for interactive chat UI.
* **JSON & CSV libraries** – for parsing and structuring data.

---

---

## 📜 License

This project is released under the **MIT License**.
Feel free to modify, extend, and use it in your own applications.
