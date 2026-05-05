#!/usr/bin/env python3
import csv
import json
import urllib.request
import ssl
from io import StringIO
from datetime import datetime

# Published Google Sheet CSV export URL
SHEET_ID = "e/2PACX-1vQEGtSnSF5xbGqJqQwNHH-c8dVPwt_8XbqQJaQsUo_bF_YD8fr3XkTVEBNFJn7x8tLgtCwLvWNMfAc8"
GID = "2021840259"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/pub?gid={GID}&single=true&output=csv"

print("Fetching data from Google Sheets...")
try:
    # Bypass SSL verification for local machines (GitHub Actions will use system certs)
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    response = urllib.request.urlopen(CSV_URL, timeout=10, context=ssl_context)
    csv_text = response.read().decode('utf-8')
except Exception as e:
    print(f"Error fetching CSV: {e}")
    exit(1)

# Parse CSV
reader = csv.reader(StringIO(csv_text))
try:
    headers = next(reader)
except StopIteration:
    print("Error: Empty CSV")
    exit(1)

# Build gviz table format
cols = [{"label": h, "type": "string"} for h in headers]
rows_data = []

for row_idx, row in enumerate(reader):
    # Pad row with empty strings if needed
    while len(row) < len(headers):
        row.append("")

    cells = []
    for col_idx, value in enumerate(row):
        cell = {"v": value if value else None}

        # Try to parse first column as date
        if col_idx == 0 and value:
            try:
                # Try common date formats
                for fmt in ["%m/%d/%Y", "%m/%d/%y", "%Y-%m-%d", "%d/%m/%Y"]:
                    try:
                        parsed = datetime.strptime(value, fmt)
                        # Convert to gviz Date format: Date(year,month0-indexed,day)
                        cell["v"] = f"Date({parsed.year},{parsed.month-1},{parsed.day})"
                        cell["f"] = parsed.strftime("%m/%d/%Y")
                        break
                    except ValueError:
                        continue
            except Exception:
                pass

        cells.append(cell)

    rows_data.append({"c": cells})

# Create gviz table
table = {
    "cols": cols,
    "rows": rows_data
}

# Write JSON
print(f"Writing {len(rows_data)} rows to data.json...")
with open('data.json', 'w') as f:
    json.dump(table, f)

print("Done!")
