import sys,os
import unittest
from unittest.mock import patch
import subprocess
import atexit
#from concurrent.futures import ThreadPoolExecutor
#import threading

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(root_dir)

from applications.basic_server.src.main.start import App

#I was having difficulties getting the rabbitMQ mocking to work and attempted to concurrently run the servers as another
#way of carrying out operations. Here is the structure of my integration test. It is a work in progress, but the goal is to
#test sending a watchlist request, having the collector gather data, and post the database to the "To Be Analyzed" directory
#----------------------------------------------------------------------------------
def run_server(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, _ = process.communicate()
    return process.returncode

def terminate_servers():
    pass
    #sys.exit(0)

def run_unittests():
    # Add a 3-second delay
    unittest.main()

def run_server_commands():
    pass
    '''with ThreadPoolExecutor(max_workers=3) as executor:
        return_codes = list(executor.map(run_server, [command1, command2, command3]))
        print("running web server:", return_codes[0])
        print("running data collector:", return_codes[1])
        print("running data analyzer:", return_codes[2])'''

#Run the test
#----------------------------------------------------------------------------------
class WebServerDataCollectorIntegrationTest(unittest.TestCase):

    def setUp(self):
        # Create a test Flask app context
        self.app_context = App.app.test_request_context()
        self.app_context.push()

    def tearDown(self):
        # Pop the Flask app context after the test
        self.app_context.pop()


    def test_web_server_data_collector_interaction(self):
        with App.app.test_client() as client:
            with patch('applications.data_collector_server.src.main.start.App.collect_data') as mock_collect_data:
                # Simulate a form request from the web server to the data collector
                #response = client.post('/process_form', data={'itemName': 'TestItem', 'zipCode': '12345'})
                directory_path = os.path.join(root_dir, 'database_storage', 'To Be Analyzed')
                file_name = 'testItem_12435.db'
                file_path = os.path.join(directory_path, file_name)

                self.assertFalse(os.path.isfile(file_path), f"Error accessing shop & creating a database for (To Be Analyzed) directory ") #change this in the future
                
#----------------------------------------------------------------------------------
if __name__ == '__main__':
    path_to_python = sys.executable

    path_to_basic_server = os.path.join(root_dir, 'applications', 'basic_server', 'src', 'main', 'start', 'App.py')
    path_to_collector_server = os.path.join(root_dir, 'applications', 'data_collector_server', 'src', 'main', 'start', 'App.py')
    path_to_analyzer_server = os.path.join(root_dir, 'applications', 'data_analyzer_server', 'src', 'main', 'start', 'App.py')

    command1 = [path_to_python, path_to_basic_server]
    command2 = [path_to_python, path_to_collector_server]
    command3 = [path_to_python, path_to_analyzer_server]

    run_unittests()
    # Use ThreadPoolExecutor to run the server commands concurrently on a separate thread
    #server_thread = threading.Thread(target=run_server_commands)
    #server_thread.start()

    # Start a thread to run the unittests concurrently
    #unittest_thread = threading.Thread(target=run_unittests)
    #unittest_thread.start()

    # Register the function to terminate servers on exit
    atexit.register(terminate_servers)

    # Wait for the threads to finish before exiting the main script
    #server_thread.join()
    #unittest_thread.join()