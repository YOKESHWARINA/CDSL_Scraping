import pandas as pd

# Specify the input CSV file and output JSON file
csv_file = r"C:\Users\Yokeshwari.7183\Desktop\NSDL Demo Project\Sample_Project\CDSL_Convertion\Output File\Final_Removed_Rows.csv"
json_file = r"C:\Users\Yokeshwari.7183\Desktop\NSDL Demo Project\Sample_Project\CDSL_Convertion\Output File\Final_Removed_Rows.json"

try:
    # Read the CSV file into a pandas dataframe
    df = pd.read_csv(csv_file, encoding='utf-8')
    
    # Verify the number of rows
    total_rows = len(df)
    print(f"Total rows in CSV: {total_rows}")
    
    if total_rows != 139045:
        print(f"Warning: Expected 139,045 rows, but found {total_rows} rows.")
    
    # Convert the dataframe to JSON
    # orient='records' creates a list of dictionaries, where each dictionary is a row
    json_data = df.to_json(orient='records', indent=4)
    
    # Save the JSON data to a file
    with open(json_file, 'w', encoding='utf-8') as f:
        f.write(json_data)
    
    print(f"Successfully converted CSV to JSON. Output saved to: {json_file}")
    
    # Optionally, print the first few records to verify
    print("\nFirst 5 records in JSON format:")
    print(json_data[:1000])  # Print first 1000 characters to avoid overwhelming output

except Exception as e:
    print(f"An error occurred: {str(e)}")