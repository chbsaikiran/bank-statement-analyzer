import json
import sys
import os
import re
from datetime import datetime

def load_transactions(json_file):
    """Load transactions from a JSON file."""
    with open(json_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_amount(value):
    """Convert a string like '  1,234.56' or '     36.00' to float safely."""
    value = value.strip().replace(',', '')
    if not value or value == '-':
        return 0.0
    try:
        return float(value)
    except ValueError:
        return 0.0


def total_net_amount(transactions):
    """Calculate net amount: Total credited (CR) - Total debited (DR)."""
    total_dr = sum(parse_amount(t.get("DR", "0")) for t in transactions)
    total_cr = sum(parse_amount(t.get("CR", "0")) for t in transactions)
    return total_cr - total_dr


def total_amount_spent(transactions):
    """Return total amount spent (sum of DR)."""
    return sum(parse_amount(t.get("DR", "0")) for t in transactions)


def total_amount_received(transactions):
    """Return total amount received (sum of CR)."""
    return sum(parse_amount(t.get("CR", "0")) for t in transactions)


def max_transaction_details(transactions):
    """Find transactions with maximum DR and maximum CR."""
    max_dr_txn = max(transactions, key=lambda t: parse_amount(t.get("DR", "0")))
    max_cr_txn = max(transactions, key=lambda t: parse_amount(t.get("CR", "0")))

    return {
        "max_DR": {
            "amount": parse_amount(max_dr_txn["DR"]),
            "PARTICULARS": max_dr_txn["PARTICULARS"]
        },
        "max_CR": {
            "amount": parse_amount(max_cr_txn["CR"]),
            "PARTICULARS": max_cr_txn["PARTICULARS"]
        }
    }


def top_transactions(transactions, top_n=10):
    """
    Get top N debit (DR) and credit (CR) transactions.
    If fewer than N exist, returns all available.
    """
    # Filter and sort by amount descending
    dr_list = [t for t in transactions if parse_amount(t.get("DR", "0")) > 0]
    cr_list = [t for t in transactions if parse_amount(t.get("CR", "0")) > 0]

    dr_sorted = sorted(dr_list, key=lambda t: parse_amount(t.get("DR", "0")), reverse=True)
    cr_sorted = sorted(cr_list, key=lambda t: parse_amount(t.get("CR", "0")), reverse=True)

    # Take top N or fewer
    top_dr = dr_sorted[:min(top_n, len(dr_sorted))]
    top_cr = cr_sorted[:min(top_n, len(cr_sorted))]

    return {"top_DR": top_dr, "top_CR": top_cr}

def get_monthly_totals(transactions, month_year=None):
    """
    Calculate total DR and CR for a given month.
    Accepts inputs like: '08-2025', '8/2025', 'Aug-2025', 'August-2025', '2025-08'.
    If no month is provided, returns totals for all data.
    """
    if not month_year:
        total_dr = total_amount_spent(transactions)
        total_cr = total_amount_received(transactions)
        return {"month": "ALL", "total_DR": total_dr, "total_CR": total_cr}

    s = str(month_year).strip()
    s = s.replace('/', '-')
    s = re.sub(r'[\u2010-\u2015]', '-', s)  # normalize fancy dashes
    s = re.sub(r'\s*-\s*', '-', s)

    fmt_candidates = ["%m-%Y", "%b-%Y", "%B-%Y", "%Y-%m"]
    month_str = None
    for fmt in fmt_candidates:
        try:
            dt = datetime.strptime(s, fmt)
            month_str = dt.strftime("%m-%Y")
            break
        except ValueError:
            continue

    if month_str is None:
        print("❌ Invalid month format! Use 'MM-YYYY' or 'Aug-YYYY'.")
        return None

    total_dr = 0.0
    total_cr = 0.0
    tx_date_formats = ["%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"]

    for t in transactions:
        date_str = str(t.get("Tran Date", "")).strip()
        if not date_str:
            continue

        date_obj = None
        for df in tx_date_formats:
            try:
                date_obj = datetime.strptime(date_str, df)
                break
            except ValueError:
                continue

        if date_obj is None:
            m = re.search(r'(\d{1,2})\D+(\d{1,2})\D+(\d{4})', date_str)
            if m:
                day, mon, year = m.groups()
                try:
                    date_obj = datetime(int(year), int(mon), int(day))
                except Exception:
                    continue

        if date_obj and date_obj.strftime("%m-%Y") == month_str:
            total_dr += parse_amount(t.get("DR", "0"))
            total_cr += parse_amount(t.get("CR", "0"))

    return {"month": month_str, "total_DR": total_dr, "total_CR": total_cr}

# ---------------- Main ----------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python get_details_from_json.py <input_json> [month-year]")
        sys.exit(1)

    json_file = sys.argv[1]
    month_year = sys.argv[2] if len(sys.argv) >= 3 else None

    if not os.path.exists(json_file):
        print(f"❌ Error: File not found -> {json_file}")
        sys.exit(1)

    transactions = load_transactions(json_file)

    print("--------------------------------------------------")
    print(f"📄 File: {json_file}")
    print("--------------------------------------------------")
    print(f"Total amount spent (DR): {total_amount_spent(transactions):,.2f}")
    print(f"Total amount received (CR): {total_amount_received(transactions):,.2f}")
    print(f"Net balance (CR - DR): {total_net_amount(transactions):,.2f}")

    details = max_transaction_details(transactions)
    print("\n💸 Max DR Transaction:")
    print(f"  Amount: {details['max_DR']['amount']}")
    print(f"  PARTICULARS: {details['max_DR']['PARTICULARS']}")
    print("\n💰 Max CR Transaction:")
    print(f"  Amount: {details['max_CR']['amount']}")
    print(f"  PARTICULARS: {details['max_CR']['PARTICULARS']}")
    print("--------------------------------------------------")

    # Top 5 DR and CR
    tops = top_transactions(transactions, top_n=20)
    print("\n🏆 Top DR Transactions:")
    for i, t in enumerate(tops["top_DR"], 1):
        print(f"  {i}. {t['Tran Date']} | Amount: {parse_amount(t['DR']):,.2f} | {t['PARTICULARS']}")

    print("\n💎 Top CR Transactions:")
    for i, t in enumerate(tops["top_CR"], 1):
        print(f"  {i}. {t['Tran Date']} | Amount: {parse_amount(t['CR']):,.2f} | {t['PARTICULARS']}")
    print("--------------------------------------------------")

    # Optional monthly summary
    monthly = get_monthly_totals(transactions, month_year)
    if monthly:
        print(f"\n📅 Totals for {monthly['month']}:")
        print(f"   Total DR: {monthly['total_DR']:,.2f}")
        print(f"   Total CR: {monthly['total_CR']:,.2f}")
    print("--------------------------------------------------")