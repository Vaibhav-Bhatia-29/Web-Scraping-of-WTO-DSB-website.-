import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

# Initialize the webdriver
driver = webdriver.Chrome(options=chrome_options)

# Create a directory to save the data
data_folder = 'wto_cases_data'
os.makedirs(data_folder, exist_ok=True)

# Function to save the case details
def save_case_details(case_number, content):
    file_name = f"ds{case_number}.html"
    file_path = os.path.join(data_folder, file_name)
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

# Iterate over the range of case numbers
for case_number in range(1, 625):
    url = f"https://www.wto.org/english/tratop_e/dispu_e/cases_e/ds{case_number}_e.htm"
    driver.get(url)
    time.sleep(2)  # Wait for the page to load

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    center_col_div = soup.find('div', class_='centerCol')

    if center_col_div:
        save_case_details(case_number, str(center_col_div))

# Close the browser
driver.quit()

print(f"Scraping completed. Data saved to '{data_folder}'.")
