import os
import pandas as pd
import re

def combine_csv_files(input_folder, output_file):
    # List all CSV files in the input directory
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]
    
    # Sort files numerically based on the page range in filenames (e.g., 1 to 10, 11 to 20)
    # Extract the starting page number from each filename for sorting
    def extract_start_page(file_name):
        match = re.search(r'pages_(\d+)_to_', file_name)
        if match:
            return int(match.group(1))  # Extract the starting page number
        return 0  # Default if no match found (shouldn't happen in this case)

    # Sort files by the starting page number
    csv_files.sort(key=extract_start_page)

    # List to hold DataFrames from each CSV
    dfs = []
    total_rows = 0  # Initialize total row counter
    
    # Read each CSV file and append its DataFrame to the list
    for file in csv_files:
        file_path = os.path.join(input_folder, file)
        try:
            # Read CSV file into DataFrame
            df = pd.read_csv(file_path)
            dfs.append(df)
            file_row_count = len(df)  # Count the number of rows in the current CSV file
            total_rows += file_row_count  # Add to total row count
            print(f"Read file: {file} - Rows: {file_row_count}")
        except Exception as e:
            print(f"Error reading {file}: {e}")
    
    # Concatenate all DataFrames into one
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        # Write the combined DataFrame to a new CSV file
        combined_df.to_csv(output_file, index=False)
        print(f"All files combined into {output_file}")
        print(f"Total rows processed: {total_rows}")  # Print total row count
    else:
        print("No CSV files found to combine.")

# Example usage
input_folder = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Output File\CSV_File_April_08"  # Replace with your folder path
output_file = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Output File\Combined_Output_April_08.csv"

combine_csv_files(input_folder, output_file)



# Example usage
#input_folder = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Output File\CSV_File_24"  # Replace with your folder path
#output_file = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Output File\combined_output.csv"  # Replace with your output file path
