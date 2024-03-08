import sys,os
import atexit
import json
from flask import Flask, request, render_template, jsonify, redirect, url_for
import pika
import threading
from copy import copy
import signal

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "..", ".."))
sys.path.append(root_dir)
from components.web_support.src.Error_Handler import Error_Handler
from applications.data_collector_server.src.main.start.App import collect_data # for integration test

lock = threading.Lock()
#app = Flask(__name__, template_folder='../resources/templates')
app = Flask(__name__, static_folder='../resources/static', template_folder='../resources/templates')
active_watchlists = []
new_items_by_watchlist ={}

#RabbitMQ Handling
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
    
def close_rabbitmq_connections():
    rabbitmq_connection.close()

def graceful_shutdown(signum, frame):
    print("Shutting down gracefully...")
    close_rabbitmq_connections()
    sys.exit(0)

#Updating Watchlists and Alerting For New Items
#----------------------------------------------------------------------------------
def listen_for_watchlist_updates():
    global active_watchlists

    directory_path = f"C:\\Users\\Jarrett\\Desktop\\CONSOLE\\School 2\\CSCA5028 ASABD\\Final\\OnlineStoreUp-Dates\\database_storage\\Watchlist"
    files = os.listdir(directory_path)
   
    active_watchlists.clear() #reset the list

    for file in files:
        search = file.split(".")[0]
        zipCode = search.split("_")[-1]
        itemName = ' '.join(search.split("_")[0:-1])
        watchlist = f"Watch set for {itemName} in {zipCode}"
        if not watchlist in active_watchlists:
            active_watchlists.append(watchlist)

def new_item_alerts(ch, method, properties, body):
    
    global new_items_by_watchlist

    message_data = json.loads(body)
    search = message_data['watchlist']
    itemName = message_data['name']
    print(itemName)
    itemPrice = message_data['price']
    itemLocation = message_data['location']
    itemURL = message_data['url']
    
    searchZip = search.split("_")[-1]
    searchItem = ' '.join(search.split("_")[0:-1])
    nameOfwatchlistOnHtml = f"Watch set for {searchItem} in {searchZip}"

    new_item_data = {
        'name': itemName,
        'price': itemPrice,
        'location': itemLocation,
        'url': itemURL
    }

    #A dictionary of watchlist names for new item storage
    if not nameOfwatchlistOnHtml in new_items_by_watchlist:
        new_items_by_watchlist[nameOfwatchlistOnHtml] = []
    if not new_item_data in new_items_by_watchlist[nameOfwatchlistOnHtml]:
        new_items_by_watchlist[nameOfwatchlistOnHtml].append(new_item_data)
    #see @app.route('/get_items')
    
    print(f"Received new item alert")
    print(new_items_by_watchlist[nameOfwatchlistOnHtml])
    #get_items()



#All Routings For HTML
#----------------------------------------------------------------------------------
@app.route('/delete_item', methods=['POST'])
def delete_item():
    try:
        data = request.get_json()
        watchlist = data.get('watchlist')
        itemName = data.get('itemName')

        return jsonify({'message': f'Item "{itemName}" from watchlist "{watchlist}" deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_items') #for updateItemCards(new items) in html
def get_items():
    try:
        global new_items_by_watchlist
        with app.app_context():
            # Get the watchlist parameter from the query string
            watchlist = request.args.get('watchlist')
            if len(new_items_by_watchlist[watchlist]) > 0:
                # Convert the set to a list before copying
                items_data = copy(list(new_items_by_watchlist[watchlist]))
                print(f"NEW ITEMS BEING SENT! {items_data}")
                # Now remove the new items acknowledged
                new_items_by_watchlist[watchlist].clear()
                return jsonify({'items': items_data})
            return jsonify({'No new items to show': 'No new items'}), 200
    except Exception as e:
        return jsonify({'No new items to show': str(e)}), 200

@app.route('/')
def new_watchlist():
    return render_template('WatchList.html', active_watchlists=active_watchlists)

@app.route('/get_watchlists')
def get_watchlists():
    listen_for_watchlist_updates() #make sure the watchlists in the file are returned at every pull
    return {'active_watchlists': active_watchlists}

@app.route('/delete_watchlist', methods=['POST'])
def delete_watchlist():
    try:
        data = request.get_json()
        watchlist = data.get('watchlist')

        # Your logic to delete the watchlist from the active_watchlists list
        if watchlist in active_watchlists:
            print(f"deleting this watchlist: {watchlist}")

            #now delete database
            watchlistClip = watchlist.split("for ")[1]
            watchlistItem = (watchlistClip.split(" in")[0]).replace(" ","_")
            watchlistZip = watchlistClip.split("in ")[1]
            search = watchlistItem + '_' + watchlistZip
            dst = f"C:\\Users\\Jarrett\\Desktop\\CONSOLE\\School 2\\CSCA5028 ASABD\\Final\\OnlineStoreUp-Dates\\database_storage\\Watchlist\\{search}.db"
            try:
                #os.unlink(dst)
                os.remove(dst)
                return jsonify({'message': f'Watchlist "{watchlist}" deleted successfully'}), 200
            except Exception as e:
                print("database could not be deleted")
                return jsonify({'error': str(e)}), 500
        else: 
            return jsonify({'error': 'Watchlist not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/process_form', methods=['POST'])
def process_form():
    if request.method == 'POST':
        # Retrieve form data
        itemName = request.form.get('itemName')
        zipCode = request.form.get('zipCode')

        if not No_Empty_Value(itemName, zipCode):
            return Error_Handler.EmptyValueError
        if not Valid_Zip_Code(zipCode):
            return Error_Handler.zipCodeError

        data = {
            'itemname': itemName, 'zipcode': zipCode
        }
        message_variables = json.dumps(data)
        rabbitmq_channel.basic_publish(exchange='', routing_key='shopping', body=message_variables)

        return redirect(url_for('new_watchlist'))

def Show_Watchlist(name, itemCount):
    return render_template('WatchList.html', active_watchlists=active_watchlists)


#User Error Handling
#----------------------------------------------------------------------------------
def Valid_Zip_Code(zc):
    if len(zc) == 5 and zc.isdigit():
        return True
    return False

def No_Empty_Value(itemName, zipCode):
    return bool(itemName and zipCode)


#init
#----------------------------------------------------------------------------------
if __name__ == "__main__":
    rabbitmq_connection, rabbitmq_channel = setup_rabbitmq()
    rabbitmq_channel.basic_consume(queue='new_items', on_message_callback=new_item_alerts, auto_ack=True)
    
    #for shutting down
    signal.signal(signal.SIGINT, graceful_shutdown)

    # Start the thread for listening for new item alerts
    new_item_thread = threading.Thread(target=rabbitmq_channel.start_consuming)
    new_item_thread.start()

    # Register the function to close RabbitMQ connections on exit
    atexit.register(close_rabbitmq_connections)
    
    app.run(debug=True, use_reloader=False)