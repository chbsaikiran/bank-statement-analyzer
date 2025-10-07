import json
import gradio as gr
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any
import re
import csv

transactions_data = []  # Will hold loaded JSON
headers_to_find = ['Tran Date', 'CHQNO', 'PARTICULARS', 'DR', 'CR', 'BAL', 'SOL']
header_alias_map = {"date":headers_to_find[0],"cheqno":headers_to_find[1],"particulars":headers_to_find[2],"dr":headers_to_find[3],"cr":headers_to_find[4],"bal":headers_to_find[5],"sol":headers_to_find[6]}

load_dotenv(override=True)

# ---------------------------
# 1. Setup LLM
# ---------------------------
llm = ChatOpenAI(model="gpt-4o-mini")

# ---------------------------
# 2. Define LangGraph Nodes
# ---------------------------

def parse_query(state):
    """Extract intent and keyword from user input"""
    query = state["input"]

    # ✅ Step 1: Try to directly extract quoted keyword
    quoted = re.findall(r"'([^']*)'|\"([^\"]*)\"", query)
    if quoted:
        # Flatten and take first non-empty match
        keyword = next((q for pair in quoted for q in pair if q), None)
        parsed = {"intent": "spending_query", "keyword": keyword}
        state["parsed"] = parsed
        return state

    # ✅ Step 2: Use LLM fallback if no quotes found
    prompt = (
        f"Extract the main keyword from this query: '{query}'. "
        "Do not include filler words like 'on', 'for', 'to'. "
        "Return a compact JSON: {\"intent\": \"spending_query\", \"keyword\": \"<keyword>\"}."
    )

    response = llm.invoke(prompt)
    try:
        parsed = json.loads(response.content)
    except Exception:
        parsed = {"intent": "spending_query", "keyword": query.strip().split()[-1]}

    state["parsed"] = parsed
    return state


def compute_spending(state):
    """Compute DR - CR based on keyword and collect matching transactions"""
    data = state["data"]
    parsed = state["parsed"]
    keyword = parsed.get("keyword", "").lower()

    total_dr, total_cr = 0.0, 0.0
    matching = []

    for t in data:
        if keyword in t[header_alias_map["particulars"]].lower():
            dr = t[header_alias_map["dr"]].strip()
            cr = t[header_alias_map["cr"]].strip()
            tran_date = t.get(header_alias_map["date"], "")
            particulars = t.get(header_alias_map["particulars"], "")

            if dr and dr != "-":
                total_dr += float(dr)
                matching.append({
                    "Tran Date": tran_date,
                    "PARTICULARS": particulars,
                    "Amount": f"₹{float(dr):,.2f} (DR)"
                })
            elif cr and cr != "-":
                total_cr += float(cr)
                matching.append({
                    "Tran Date": tran_date,
                    "PARTICULARS": particulars,
                    "Amount": f"₹{float(cr):,.2f} (CR)"
                })

    state["result"] = total_dr - total_cr
    state["matching"] = matching
    return state


def respond(state):
    """Generate final response including transaction list"""
    keyword = state["parsed"].get("keyword", "")
    result = state["result"]
    matching = state["matching"]

    # Prepare summary message
    if result > 0:
        message = f"💸 You spent **₹{result:,.2f}** on **{keyword}**.\n\n"
    elif result < 0:
        message = f"💰 You gained **₹{abs(result):,.2f}** from **{keyword}**.\n\n"
    else:
        message = f"No transactions found for '{keyword}'."
        state["output"] = message
        return state

    # Add matching transaction table
    if matching:
        table_rows = "\n".join(
            [f"- 📅 {t['Tran Date']} | {t['PARTICULARS']} | {t['Amount']}" for t in matching]
        )
        message += f"**Matching Transactions:**\n{table_rows}"
    else:
        message += "_No detailed transactions found._"

    state["output"] = message
    return state


# ---------------------------
# 3. Define State Schema
# ---------------------------
class TransactionState(TypedDict):
    input: str
    data: List[Dict[str, Any]]
    parsed: Dict[str, Any]
    result: float
    matching: List[Dict[str, Any]]
    output: str


# ---------------------------
# 4. Build LangGraph pipeline
# ---------------------------
graph = StateGraph(TransactionState)

graph.add_node("parse_query", parse_query)
graph.add_node("compute_spending", compute_spending)
graph.add_node("respond", respond)

graph.add_edge("parse_query", "compute_spending")
graph.add_edge("compute_spending", "respond")
graph.add_edge("respond", END)
graph.set_entry_point("parse_query")

app = graph.compile()

# ---------------------------
# 5. Gradio Chat Interface
# ---------------------------

def parse_csv_to_json(csv_file_path, header_identifiers):
    """
    Reads a CSV file, finds the row containing specific header identifiers,
    and from the next row onwards, converts each row into a JSON object.
    Adds a field 'withdrawal_or_deposit' based on which column (withdrawal/deposit) has data.

    Args:
        csv_file_path (str): Path to the CSV file.
        header_identifiers (list): List of column names to identify header row (e.g. ['Date', 'Withdrawal', 'Deposit'])

    Returns:
        list: List of JSON objects (dictionaries)
    """

    json_data = []
    header_row_index = None
    headers = None

    # Read CSV file
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = list(csv.reader(csvfile))

        # Step 1: Find the header row
        for i, row in enumerate(reader):
            if all(col in row for col in header_identifiers):
                header_row_index = i
                headers = row
                break

        if header_row_index is None:
            raise ValueError("Header row with specified columns not found.")

        # Step 2: Parse subsequent rows
        for row in reader[header_row_index + 1:]:
            if len(row) < len(headers):
                continue  # skip incomplete rows

            record = dict(zip(headers, row))

            json_data.append(record)

    return json_data

def upload_json(file):
    global transactions_data
    global headers_to_find
    if file is None:
        return "⚠️ Please upload a .csv file with transactions."
    transactions_data = parse_csv_to_json(file.name,headers_to_find)
    return f"✅ Loaded {len(transactions_data)} transactions successfully!"

def chat_with_agent(message, history):
    if not transactions_data:
        return "⚠️ Please upload your transaction JSON first."
    response = app.invoke({"input": message, "data": transactions_data})
    return response["output"]

with gr.Blocks() as demo:
    gr.Markdown("# 💬 Bank Transaction Analyzer (LangGraph + Gradio)")
    gr.Markdown("Upload your JSON and ask questions like:")
    gr.Markdown("- *How much did I spend on rent?*  \n- *How much did I get from salary?*")

    upload_btn = gr.File(label="Upload your transactions JSON")
    upload_output = gr.Textbox(label="Status", interactive=False)
    upload_btn.change(upload_json, upload_btn, upload_output)

    gr.ChatInterface(fn=chat_with_agent, title="Transaction Chat Agent")

# ---------------------------
# 6. Launch in Browser
# ---------------------------
demo.launch(inbrowser=True)
