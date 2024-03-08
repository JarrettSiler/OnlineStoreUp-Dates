import sys, os, time
import pika
import json
import shutil
import threading
import signal

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", ".."))
sys.path.append(root_dir)

from components.data_collector.src.Retrieve_Listings import Retrieve_Listings
from components.data_analyzer.src import Database_Handler 
from applications.basic_server.src.main.start import App

running = True
lock = threading.Lock() #added to combat race issue


#RabbitMQ and Graceful Quitting Handling
#----------------------------------------------------------------------------------
def setup_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
        channel = connection.channel()
        channel.queue_declare(queue='shopping')
        channel.queue_declare(queue='new_items')
        channel.basic_qos(prefetch_count=1)

        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ. Is it running? : {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None

def reconnect_to_rabbitmq():
    global rabbitmq_connection, rabbitmq_channel
    rabbitmq_connection, rabbitmq_channel = setup_rabbitmq()

def signal_handler(signal, frame):
    global running
    print("Ctrl+C pressed. Exiting...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

#Check For Databases to Handle in "To Be Analyzed" and checks if new items were added
#----------------------------------------------------------------------------------
def monitor_directory(directory_path, indicator: str): #acknowledges databases in "To Be Analyzed", sends them to check_database()
    global running
    while running:
        with lock: #added to combat race issue
            # List all files in the directory
            files = os.listdir(directory_path)
            # Process the files as needed
            for file in files:
                #if not file == "testitemdatabase1122_80301.db": #dont operate on the test file
                search = file.split(".")[0]
                print(f"Checking Database: {file}")
                check_database(search) #checks to see if new items were added to the database
        
        #testing case
        if indicator == 'test':
            break
            # Add a delay between iterations
        time.sleep(5)

def check_database(search): #checks to see if the database already exists in the "Watchlist" directory, if it does, checks to see if new items were added
    if Database_Handler.is_existing(search):
        
        new_items = Database_Handler.check_for_new_items(search)
        if len(new_items) > 0: #when new items are found, send them via MQ to the web server
            for item1 in new_items: 
                watchlist = search
                name = item1[0]
                price = item1[1]
                location = item1[3]
                url = item1[4]
                send_new_items_to_web(watchlist,name,price,location,url) #the method that sends new items via MQ

        if len(new_items) == 0:
            print(f"No new items found for {search}")

    src = os.path.join(root_dir, 'database_storage', 'To Be Analyzed', f"{search}.db")
    dst = os.path.join(root_dir, 'database_storage', 'Watchlist', f"{search}.db")

    shutil.copy2(src,dst) #copies catabase from "To Be Analyzed" to "Watchlist"
    print(f"Database {search} up to date")
    os.remove(src) #Deletes the watchlist in "To Be Analyzed"

def send_new_items_to_web(watchlist,name,price,location,url): #the method that sends new items via MQ
    try: #handle connection errors
        data = {
            'watchlist': watchlist, 'name': name,
            'price': price, 'location': location, 'url': url
        }
        message_variables = json.dumps(data)

        rabbitmq_channel.basic_publish(exchange='', routing_key='new_items', body=message_variables)
        print(f"New items found for {watchlist}, sent alert")

    except pika.exceptions.StreamLostError as e:
        print(f"Connection lost: {e}")
        reconnect_to_rabbitmq()


#sends each database existing in the "Watchlist" directory back into the data collector
#----------------------------------------------------------------------------------
def automatic_database_updater(directory_path, timeTS:int, testing:str):
    global running
    while running:
        time.sleep(timeTS) # how often the lists are updated from online source - in real world application, 3 times a day?
        
        if testing == 'test': #testing case
            break

        #with lock: #added to combat race issue
        files = os.listdir(directory_path)

        for file in files:
            search = file.split(".")[0]
            searchZip = search.split("_")[-1]
            searchItem = ' '.join(search.split("_")[0:-1])
            print(f"Checking For Updates- Database: {search}")

            try: #handle connection errors
                #send existing database to collector to check for new items
                data = {
                    'itemname': searchItem, 'zipcode': searchZip
                }
                message_variables = json.dumps(data) # Serialize the data to JSON

                rabbitmq_channel.basic_publish(exchange='', #validations passed, send the values to the queue
                            routing_key='shopping',
                            body=message_variables)
            except pika.exceptions.StreamLostError as e:
                print(f"Connection lost: {e}")
                reconnect_to_rabbitmq()
                        
#init
#----------------------------------------------------------------------------------
if __name__ == '__main__':

    rabbitmq_connection, rabbitmq_channel = setup_rabbitmq()

    print(' [*] Waiting for database to analyze. To exit press CTRL+C')
    directory_to_monitor = os.path.join(root_dir, 'database_storage', 'To Be Analyzed')
    directory_to_upkeep = os.path.join(root_dir, 'database_storage', 'Watchlist')

    #run in parallel
    thread_one = threading.Thread(target=monitor_directory, args=(directory_to_monitor, 'run'))
    thread_two = threading.Thread(target=automatic_database_updater, args=(directory_to_upkeep, 30, 'run')) #time between automatic checks is set here
    thread_one.start()
    thread_two.start()
    
    while running:
        time.sleep(1)