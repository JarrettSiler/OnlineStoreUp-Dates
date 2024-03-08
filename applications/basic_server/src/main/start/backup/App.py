import sys,os, time
import atexit
import json
from flask import Flask, request, render_template, jsonify, redirect, url_for, Response
from flask import stream_with_context, render_template_string
import pika
import threading

sys.path.append(r'C:\Users\Jarrett\Desktop\CONSOLE\School 2\CSCA5028 ASABD\Final\OnlineStoreUp-Dates')
from components.web_support.src.Error_Handler import Error_Handler

lock = threading.Lock()
app = Flask(__name__, template_folder='../resources/templates')
active_watchlists = []

def setup_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672))
        channel = connection.channel()
        channel.queue_declare(queue='shopping')
        channel.queue_declare(queue='new_items')
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Error connecting to RabbitMQ. Is it running? : {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None, None


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
    message_data = json.loads(body)

    search = message_data['watchlist']
    searchZip = search.split("_")[-1]
    searchItem = ' '.join(search.split("_")[0:-1])
    watchlist = f"Watch set for {searchItem} in {searchZip}"

    print(f"sending new item to: {watchlist}")

    # Notify the client using SSE
    event_data = {
        'type': 'new_item_alert',
        'data': message_data,
    }
    send_sse(event_data)

sse_clients = []

def send_sse(data):
    event_string = f"data: {json.dumps(data)}\n\n"
    for client in sse_clients:
        try:
            client.send(event_string)
        except Exception as e:
            print(f"Error sending SSE to client: {e}")

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name)
    rv = t.stream(context)
    rv.enable_buffering(5)
    return rv



@app.route('/delete_item', methods=['POST'])
def delete_item():
    try:
        data = request.get_json()
        watchlist = data.get('watchlist')
        itemName = data.get('itemName')

        # Add your logic to delete the item from the backend or perform any other necessary actions
        # ...

        return jsonify({'message': f'Item "{itemName}" from watchlist "{watchlist}" deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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
    
def event_stream():
    # Notify the client that the connection is established
    yield "data: Connected\n\n"

    # Add the client to the list of SSE clients
    client = request.environ['wsgi.websocket']
    sse_clients.append(client)

    try:
        while True:
            # Keep the connection open
            time.sleep(1)
    except Exception as e:
        print(f"Client disconnected: {e}")
    finally:
        # Remove the client from the list upon disconnection
        sse_clients.remove(client)

@app.route('/stream')
def stream():
    return Response(event_stream(), content_type='text/event-stream')






def Show_Watchlist(name, itemCount):
    return render_template('WatchList.html', active_watchlists=active_watchlists)

def Valid_Zip_Code(zc):
    if len(zc) == 5 and zc.isdigit():
        return True
    return False

def No_Empty_Value(itn, zc):
    if len(itn) == 0 or len(zc) == 0:
        return False
    return True

def close_rabbitmq_connections():
    rabbitmq_connection.close()

if __name__ == "__main__":
    rabbitmq_connection, rabbitmq_channel = setup_rabbitmq()
    rabbitmq_channel.basic_consume(queue='new_items', on_message_callback=new_item_alerts, auto_ack=True)
    
    # Start the thread for listening for new item alerts
    new_item_thread = threading.Thread(target=rabbitmq_channel.start_consuming)
    new_item_thread.start()

    # Register the function to close RabbitMQ connections on exit
    atexit.register(close_rabbitmq_connections)
    
    app.run(debug=True)