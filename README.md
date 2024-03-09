# OnlineStoreUp-Dates
5028 final - running instructions below
Use https://mock-shopping-site-5028-f2a357aaa859.herokuapp.com/ concurrently to test 
------------------------------------------------------------------------------------------------------------------------------
The following application uses 3 servers to complete a web scraping and monitoring task.

-The web server uses flask to load html and listen for input, rabbitmq to send requested watchlists to the data collector and to listen for new items from the data analyzer (so that it can display them on the html)

-The data collector receives watchlist requests from rabbitmq and will collect data (items for sale) from an online store matching item names and zip code specified by the watchlist. Furthermore, it will create a database   for said items.

-The data analyzer monitors the watchlist databases delivered by the collector and compares the items in the database to an existing databases (if there are any)- sending new items added via rabbitmq to the web server and sending requests to the data collector in the same rabbitmq queue that the web server sends requests in (that way the items are gathered from the shopping site again - in case a new item was added)

----------------------------------------------------------------------------------
Database directory:

the created databases will rotate between 3 states:

-Temporary (where information goes during scrape)
-To Be Analyzed (Where the Data Collector queues up databases for analysis)
-Watchlist (The final product of each database)

Each state has a directory underneath the root_directory/database_storage
(observe during run)

----------------------------------------------------------------------------------
CI/CD
----------------------------------------------------------------------------------
Unit tests:
Unit tests are performed in a workflow through github actions using directory /github.io/workflows/unit_tests.yml
unit tests are presented near each "App.py" as a "AppTest.py"

Integration tests:
Integration tests are performed in a workflow through github actions using directory /github.io/workflows/integration_tests.yml
Integration tests for the application are located in: /integration_tests/ directory

----------------------------------------------------------------------------------

To Use The Application
----------------------------------------------------------------------------------
Run RabbitMQ and each of the 3 server's App.py files.

If running app environment through docker-compose up, use http://localhost:5000/ to access the web server's html and create watchlists. Run by navigating to project and using "docker-compose up" - not working propertly, use other method

If running local through seperate cmd prompt windows (Run the 3 App.py files seperately), use http://127.0.0.1:5000/ to access the web server's html and create watchlists (see instructions below)

----------------------------------------------------------------------------------
HOW TO RUN LOCAL- pref

download the required plugins in requirements.txt
in any directory on cmd prompt:
docker pull rabbitmq:3-management
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
in project directory:
terminal window 1: path of basic_server App.py file: python App.py
terminal window 2: path of data_collector_server App.py file: python App.py
terminal window 3: path of data_analyzer_server App.py file: python App.py

1. Navigate to either http://127.0.0.1:5000/ or http://localhost:5000/
2. create a watchlist
3. wait for watchlist to become available underneath "Active Watchlists" area. This can take up to two minutes
4. Navigate to https://mock-shopping-site-5028-f2a357aaa859.herokuapp.com/ and simulate multiple items being added (add a couple, the site is buggy)
    In the backend, the data analyzer is continuously checking the "Mock online store" for new items (This mock store was created to simulate items being added)
5. New item alerts will be created on the right side of the webpage underneath "Notifications" 

Notes:

-watchlists take roughly 1-2 minutes to complete a full update cycle. If you add items to the online store, notifications will appear anywhere within this time. If you remove items from the store (please press button multiple times, it is buggy) it will take roughly the same amount of time to process an updated database.

-Watchlists may come back after being deleted. This is due to the frequency that they are updated. In a real world scenario, the data analyzer would operate on a database up to three times a day, and deleting the database would not be difficult as it would be stationary in the Watchlist file.