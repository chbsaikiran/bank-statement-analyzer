import csv
import json
import sys
import os

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

            # Step 3: Add withdrawal_or_deposit flag
            withdrawal_val = record.get('DR', '').strip()
            deposit_val = record.get('CR', '').strip()

            record['withdrawal_or_deposit'] = True if withdrawal_val else False

            json_data.append(record)

    return json_data


# Example usage:
if __name__ == "__main__":
    # --- Accept arguments from command line ---
    if len(sys.argv) < 2:
        print("Usage: python create_json_from_csv.py <input_csv> [output_json]")
        sys.exit(1)

    csv_file = sys.argv[1]

    if not os.path.exists(csv_file):
        print(f"❌ Error: File not found -> {csv_file}")
        sys.exit(1)

    # Derive output name
    if len(sys.argv) >= 3:
        json_file = sys.argv[2]
    else:
        json_file = os.path.splitext(csv_file)[0] + ".json"

    headers_to_find = ['Tran Date', 'CHQNO', 'PARTICULARS', 'DR', 'CR', 'BAL', 'SOL']

    try:
        data = parse_csv_to_json(csv_file, headers_to_find)
    except Exception as e:
        print(f"❌ Error while parsing CSV: {e}")
        sys.exit(1)

    # Save JSON
    with open(json_file, "w", encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4, ensure_ascii=False)

    print(f"✅ JSON file created successfully: {json_file}")
