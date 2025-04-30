import pdfplumber
import json
import re

def clean_and_split_line(line):
    """Cleans and splits a line with irregular spaces or special symbols."""
    cleaned_line = re.sub(r'\s{2,}', '|', line.strip())
    return cleaned_line.split('|')

def parse_text_to_table(text, header):
    """Fallback: Parse plain text to extract table data if table extraction fails."""
    lines = text.split("\n")
    data = []
    for line in lines:
        row_data = clean_and_split_line(line)
        if len(row_data) < len(header):
            row_data += [None] * (len(header) - len(row_data))
        elif len(row_data) > len(header):
            row_data = row_data[:len(header)]
        record = {header[i]: row_data[i] for i in range(len(header))}
        data.append(record)
    return data

def sanitize_header(header):
    """Sanitize and normalize column names."""
    sanitized_header = []
    seen_columns = set()
    for col in header:
        col_name = col.strip() if col else "Unnamed_Column"
        if col_name in seen_columns:
            suffix = 1
            new_col_name = f"{col_name}_{suffix}"
            while new_col_name in seen_columns:
                suffix += 1
                new_col_name = f"{col_name}_{suffix}"
            col_name = new_col_name
        seen_columns.add(col_name)
        sanitized_header.append(col_name)
    return sanitized_header

def is_invalid_header(header):
    """Check if the header is invalid (numeric, blank, or inconsistent)."""
    if all(col.isdigit() or not col.strip() for col in header):
        return True
    if len(set(header)) < 3:
        return True
    return False

def extract_pdf_to_json(pdf_path, output_json_path, start_page=1, end_page=50, custom_header=None):
    """Extract tables and text from a PDF and save as JSON. Returns count of extracted records."""
    data = []
    last_valid_header = custom_header if custom_header else None

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"📄 Total pages in PDF: {total_pages}")
        
        if start_page > total_pages or end_page > total_pages or start_page > end_page:
            print(f"⚠️ Invalid page range: {start_page}-{end_page}. PDF has only {total_pages} pages.")
            return 0

        for page_number, page in enumerate(pdf.pages[start_page - 1:end_page], start=start_page):
            print(f"🔎 Processing page {page_number}...")
            tables = page.extract_tables({
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "snap_tolerance": 2,
                "join_tolerance": 2,
                "intersection_tolerance": 2,
            })

            if tables:
                for table in tables:
                    if table:
                        if custom_header:
                            header = custom_header
                        else:
                            new_header = sanitize_header(table[0])
                            if is_invalid_header(new_header) or len(new_header) < 3:
                                print(f"⚠️ Invalid header on page {page_number}. Using previous header.")
                                header = last_valid_header
                            else:
                                header = new_header
                                last_valid_header = header

                        if header:
                            for row in table[1:]:
                                if len(row) < len(header):
                                    row += [None] * (len(header) - len(row))
                                elif len(row) > len(header):
                                    row = row[:len(header)]
                                record = {header[idx]: row[idx].strip() if row[idx] else None for idx in range(len(header))}
                                data.append(record)
            else:
                print(f"⚠️ No table found on page {page_number}, attempting text extraction...")
                raw_text = page.extract_text()
                if raw_text and last_valid_header:
                    parsed_data = parse_text_to_table(raw_text, last_valid_header)
                    if parsed_data:
                        data.extend(parsed_data)

    after_extraction_count = len(data)
    print(f"✅ Extracted {after_extraction_count} records")
    
    if data:
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4, ensure_ascii=False)
        print(f"✅ Data saved to '{output_json_path}'")
    return after_extraction_count

# Custom header definition
custom_header = [
    "Sr.no", "Client PAN", "Column Name", "Level of Freeze", "Remarks", 
    "Order Date", "Client Address", "Whether PAN is debarred for opening of new account"
]

# PDF path
pdf_path = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Output File\CDSL_Report_2025-03-21.pdf"

# Process multiple page ranges efficiently
page_ranges = [
    (1, 50, "output_data1_50.json"),
    (51, 100, "output_data51_100.json"),
    (101, 150, "output_data101_150.json"),
    (151, 200, "output_data151_200.json"),
    (201, 250, "output_data201_250.json"),
    (251, 300, "output_data251_300.json"),
    (301, 350, "output_data301_350.json"),
    (351, 400, "output_data351_400.json"),
    (401, 450, "output_data401_450.json"),
    (451, 500, "output_data451_500.json"),
    (501, 548, "output_data501_548.json")
]

# Execute extraction for all ranges and store results
results = {}
base_output_path = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Output File"
for start, end, filename in page_ranges:
    output_path = f"{base_output_path}\{filename}"
    print(f"🔢 Extracting records from pages {start} to {end}...")
    count = extract_pdf_to_json(pdf_path, output_path, start_page=start, end_page=end, custom_header=custom_header)
    results[f"{start}_{end}"] = count

# Print final results
for start, end, _ in page_ranges:
    print(f"📊 Total records extracted from pages {start} to {end}: {results[f'{start}_{end}']}")