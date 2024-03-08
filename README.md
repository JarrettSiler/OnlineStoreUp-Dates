# OnlineStoreUp-Dates
5028 final
------------------------------------------------------------------------------------------------------------------------------
The following application uses 3 servers to complete a web scraping and monitoring task.

-The web server uses flask to load html and listen for input, rabbitmq to send requested watchlists to the data collector and to listen for new items from the data analyzer (so that it can display them on the html)

-The data collector receives watchlist requests from rabbitmq and will collect data (items for sale) from an online store matching item names and zip code specified by the watchlist. Furthermore, it will create a database   for said items.

-The data analyzer monitors the watchlist databases delivered by the collector and compares the items in the database to an existing databases (if there are any)- sending new items added via rabbitmq to the web server and sending requests to the data collector in the same rabbitmq queue that the web server sends requests in (that way the items are gathered from the shopping site again - in case a new item was added)


CI/CD
------------------------------------------------------------------------------------------------------------------------------
Unit tests:
Unit tests are performed in a workflow through github actions using directory /github.io/workflows/unit_tests.yml
unit tests are presented near each "App.py" as a "AppTest.py"

Integration tests:
Integration tests are performed in a workflow through github actions using directory /github.io/workflows/integration_tests.yml
Integration tests for the application are located in: /integration_tests/ directory

------------------------------------------------------------------------------------------------------------------------------
