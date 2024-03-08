from bs4 import BeautifulSoup as bs #for navigating the HTML
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')

sys.path.append(r'C:\Users\Jarrett\Desktop\CONSOLE\School 2\CSCA5028 ASABD\Final\OnlineStoreUp-Dates')

# Now try importing your module
from components.data_collector.src.Listing import Listing #TODO -fix imports for docker use

class Retrieve_Listings:
    def __init__(self, item: str, zipCode: str):
 #converts item format to a string that is in searchable format for offer-up API
        self.zipCode = zipCode
        self.item = item
            
    def get_listings(self):

        URL = "https://mock-shopping-site-5028-f2a357aaa859.herokuapp.com/"
        driver = webdriver.Chrome(options=chrome_options)  # Use the appropriate webdriver for your browser
        driver.delete_all_cookies()
        driver.get(URL)

        # Wait until the "zipCodeInput" element is accessible
        zip_code_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "zipCodeInput"))
        )

        zip_code_input.send_keys(self.zipCode)
        zip_code_input.send_keys(Keys.ENTER)
        html_source = driver.page_source

        driver.quit()

        soup = bs(html_source, "html.parser")
        div_tag = soup.find('div', {'id': 'itemList'})
        return div_tag.find_all('div', class_='item')
        #the goal here is to return a list of objects with item name, price, location, and extra details
