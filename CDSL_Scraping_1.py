import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pikepdf  # To validate the PDF file

# Set download directory
download_directory = r"C:\Users\Yokeshwari.7183\Desktop\CDSL Django\PDF_Convertion\Input File"
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Configure Chrome options
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": download_directory,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

# Initialize WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    driver.maximize_window()
    print("Navigating to CDSL website")
    driver.get("https://www.cdslindia.com/Publications/periodicstats.aspx")

    # Wait for and click the image (or use the correct link)
    print("Waiting for image to be clickable")
    pdf_click = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "(//li[@class='col-lg-12 col-md-12 col-sm-12 p-0'])[2]//img"))
    )
    pdf_click.click()

    # Wait for download to complete (check file size to confirm)
    print("Waiting for download to complete")
    timeout = 30
    start_time = time.time()
    downloaded_pdf = None

    while time.time() - start_time < timeout:
        downloads = [f for f in os.listdir(download_directory) if f.endswith('.pdf')]
        if downloads:
            downloaded_pdf = downloads[0]
            downloaded_pdf_path = os.path.join(download_directory, downloaded_pdf)
            
            # Check if the file is fully downloaded (size remains constant)
            initial_size = os.path.getsize(downloaded_pdf_path)
            time.sleep(2)  # Wait a bit more
            final_size = os.path.getsize(downloaded_pdf_path)
            
            if initial_size == final_size:
                break
        time.sleep(1)

    if not downloaded_pdf:
        raise Exception("Download timed out or failed")

    # Get current date
    current_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Current date: {current_date}")

    # Get downloaded file path
    downloaded_pdf_path = os.path.join(download_directory, downloaded_pdf)

    # Define and ensure unique new file name
    base_name = f"CDSL_Report_{current_date}"
    new_pdf_name = f"{base_name}.pdf"
    new_pdf_path = os.path.join(download_directory, new_pdf_name)
    counter = 1
    while os.path.exists(new_pdf_path):
        new_pdf_name = f"{base_name}_{counter}.pdf"
        new_pdf_path = os.path.join(download_directory, new_pdf_name)
        counter += 1

    # Validate PDF to check if it's valid
    try:
        with pikepdf.open(downloaded_pdf_path):
            print("PDF is valid!")
    except pikepdf.PdfError as e:
        raise Exception(f"Error opening PDF: {e}")

    # Rename the file
    os.rename(downloaded_pdf_path, new_pdf_path)
    print(f"File renamed to: {new_pdf_name}")

finally:
    driver.quit()
