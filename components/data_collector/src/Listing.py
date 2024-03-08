from bs4 import BeautifulSoup as bs #for navigating the HTML

class Listing:
    def __init__(self, soup: bs):

        p_tags = soup.find_all('p')

        price_text = p_tags[0].get_text()
        self.price = price_text.split(':')[-1].strip()

        self.info = p_tags[1].get_text()
 
        location_text = p_tags[2].get_text()
        self.location = location_text.split(':')[-1].strip()

        self.title = soup.find('h2').text.strip()

    def get_item_name(self):
        return self.title
    
    def get_price(self):
        return self.price
    
    def get_location(self):
        return self.location
    
    def get_additional_info(self):
        return self.info
    
    def get_URL(self):
        return 'example URL'
