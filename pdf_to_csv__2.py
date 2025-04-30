import camelot
import pandas as pd
import os
from multiprocessing import Pool, cpu_count
from functools import partial


def clean_merged_rows(df):
    """Clean up merged rows by splitting improperly concatenated rows."""
    cleaned_rows = []
    for index, row in df.iterrows():
        merged_cells = [cell for cell in row if isinstance(cell, str) and len(cell.split(',')) > 1]
        if merged_cells:
            # Split and expand merged rows
            split_rows = [cell.split(',') if isinstance(cell, str) else [cell] for cell in row]
            split_rows = list(map(list, zip(*split_rows)))  # Transpose to correct shape
            cleaned_rows.extend(split_rows)
        else:
            cleaned_rows.append(row.tolist())
    return pd.DataFrame(cleaned_rows)


def process_table_chunk(chunk_info, pdf_path, output_dir):
    """Process a chunk of pages and save tables to a single CSV."""
    start_page, end_page = chunk_info
    chunk_range = f"{start_page}-{end_page}"

    try:
        # Try extracting tables using lattice mode
        tables = camelot.read_pdf(
            pdf_path,
            pages=chunk_range,
            flavor="lattice",
            suppress_stdout=True,
            strip_text='\n',
            split_text=True,  # Prevents merged rows
            line_scale=40,  # Helps with complex layouts
            shift_text=['', ' ']  # Reduces unwanted merges
        )

        # If no tables found, switch to stream mode
        if len(tables) == 0:
            print(f"No tables found with lattice. Switching to stream mode for pages {chunk_range}")
            tables = camelot.read_pdf(
                pdf_path,
                pages=chunk_range,
                flavor="stream",
                suppress_stdout=True,
                strip_text='\n',
                split_text=True
            )

        if len(tables) == 0:
            print(f"No tables found in pages {chunk_range}")
            return 0

        # Combine all tables in this chunk into one DataFrame
        combined_df = pd.concat([table.df for table in tables], ignore_index=True)

        # Clean any merged rows
        combined_df = clean_merged_rows(combined_df)

        # Remove duplicates to avoid merging issues
        combined_df = combined_df.drop_duplicates()

        # Define output filename for this chunk
        output_csv = os.path.join(output_dir, f"pages_{start_page}_to_{end_page}_table.csv")

        # Save the combined table to CSV
        combined_df.to_csv(output_csv, mode='w', index=False, quoting=1, lineterminator='\n')
        print(f"Saved tables from pages {start_page} to {end_page} to {output_csv}")

        return len(combined_df)  # Return row count for tracking

    except Exception as e:
        print(f"Error processing pages {chunk_range}: {e}")
        return 0


def extract_and_save(pdf_path, output_dir):
    """Extract tables from PDF and save 10 pages per CSV file."""
    print("Starting PDF extraction...")

    # Create output directory if it doesn’t exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        # Define page ranges for 548 pages (in chunks of 10 pages)
        chunk_size = 10
        page_chunks = [
            (start, min(start + chunk_size - 1, 548)) 
            for start in range(1, 549, chunk_size)
        ]
        # Results in: [(1, 10), (11, 20), ..., (541, 548)]

        # Use multiprocessing to process chunks in parallel
        num_cores = min(cpu_count(), len(page_chunks))
        print(f"Using {num_cores} CPU cores for parallel processing...")

        with Pool(processes=num_cores) as pool:
            process_partial = partial(process_table_chunk, pdf_path=pdf_path, output_dir=output_dir)
            row_counts = pool.map(process_partial, page_chunks)

        # Summary
        total_rows = sum(row_counts)
        if total_rows == 0:
            print("No tables found in the PDF.")
            return
        
        print(f"All tables processed and saved to CSV files in {output_dir}")
        print(f"Total rows processed: {total_rows}")
        print(f"Total chunks processed: {len(page_chunks)}")

    except Exception as e:
        print(f"Error processing the PDF: {e}")

    # Check total size of all CSV files
    total_size_mb = 0
    for file in os.listdir(output_dir):
        if file.endswith(".csv"):
            total_size_mb += os.path.getsize(os.path.join(output_dir, file)) / (1024 * 1024)
    print(f"Total size of all CSV files: {total_size_mb:.2f} MB")


if __name__ == "__main__":
    # PDF file path
    pdf_path = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Input File\CDSL_Report_2025-04-08.pdf"

    # Output directory
    output_dir = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Scraping\Output File\CSV_File_April_08"
    
    # Run the extraction
    extract_and_save(pdf_path, output_dir)
