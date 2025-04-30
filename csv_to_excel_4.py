import pandas as pd

def csv_to_excel(input_csv_file, output_excel_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_csv_file)

    # Convert the DataFrame to Excel format and save it
    df.to_excel(output_excel_file, index=False)  # index=False prevents writing row indices

    print(f"CSV file '{input_csv_file}' has been converted to Excel file '{output_excel_file}'.")

# Example usage
input_csv_file = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Output File\Combined_Output_April_08.csv"  # Replace with your input CSV file path
output_excel_file = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Output File\Combined_Output_April_08.xlsx"  # Replace with your desired Excel file path

csv_to_excel(input_csv_file, output_excel_file)
