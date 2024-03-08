import sys,os
import shutil
from sqlalchemy import create_engine, Column, String, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pika
from pika import BlockingConnection
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", ".."))
sys.path.append(root_dir)

from components.data_collector.src.Retrieve_Listings import Retrieve_Listings
from components.data_collector.src.Listing import Listing

Base = declarative_base()

#database creation
#----------------------------------------------------------------------------------
# Specify the absolute path to the directory where you want to store the database file
db_file_path = os.path.join(root_dir, 'database_storage', 'Temporary', 'tmp.db')

# Create the engine with the updated file path
engine = create_engine(f"sqlite:///{db_file_path}", echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

class dbEntry(Base):
    __tablename__ = 'Listings'

    itemName = Column('itemName', String, primary_key=True)
    itemPrice = Column('itemPrice', String)
    itemLocation = Column('itemLocation', String)
    itemInfo = Column('itemInfo', String)
    itemURL = Column('itemURL', String)

    def __init__(self, itemName, itemPrice, itemLocation, itemInfo, itemURL):
        self.itemName = itemName
        self.itemPrice = itemPrice
        self.itemLocation = itemLocation
        self.itemInfo = itemInfo
        self.itemURL = itemURL

    def __repr__(self):
        return f"{self.itemName} {self.itemPrice} {self.itemLocation} {self.itemInfo} {self.itemURL}"
    
def truncate_db(engine):
    # delete all table data (but keep tables)
    meta = MetaData()
    meta.reflect(bind=engine)
    con = engine.connect()
    trans = con.begin()

    for table in reversed(meta.sorted_tables):  # Reverse the order to handle foreign key constraints
        con.execute(table.delete())
    trans.commit()

def collect_data(item: str, zc: str):
    
    truncate_db(engine)
    listings = Retrieve_Listings(item, zc).get_listings()

    for listing in listings:
        listingInfo = Listing(listing)

        listingVariables = dbEntry(
            listingInfo.get_item_name(),
            listingInfo.get_price(),
            listingInfo.get_location(),
            listingInfo.get_additional_info(),
            listingInfo.get_URL()
        )
        session.add(listingVariables)
        session.commit()
    session.close()
    engine.dispose()
    #move and rename the database now that it is finalized
    src = os.path.join(root_dir, 'database_storage', 'Temporary', 'tmp.db')
    dst = os.path.join(root_dir, 'database_storage', 'To Be Analyzed', f"{item.replace(' ', '_')}_{zc}.db")
    shutil.copy2(src,dst)


#process from MQ
#----------------------------------------------------------------------------------
def callback(ch, method, properties, body):
    process_message(body)

def process_message(body):
    message_data = json.loads(body)
    item_to_search_for = message_data['itemname']
    zip_code_to_search_in = message_data['zipcode']

    collect_data(item_to_search_for, zip_code_to_search_in)


#init
#----------------------------------------------------------------------------------
if __name__ == '__main__':

    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq', 5672)) #TODO - replace with localhost
    channel = connection.channel()
    channel.queue_declare(queue='shopping')

    channel.basic_qos(prefetch_count=1) #consume one message at a time (make sure the temp database is not saturated by multiple requests running synchronously)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.basic_consume(queue='shopping', on_message_callback=callback, auto_ack=True)
    channel.start_consuming()