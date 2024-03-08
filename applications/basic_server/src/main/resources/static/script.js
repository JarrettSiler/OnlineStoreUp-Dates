
// html page js

function updateWatchlists() {
    fetch('/get_watchlists')
        .then(response => response.json())
        .then(data => {
            const watchlistList = document.getElementById('watchlistList');
            watchlistList.innerHTML = ''; // Clear existing list

            data.active_watchlists.forEach(watchlist => {
                const listItem = document.createElement('li');

                // Create a delete button
                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Delete';
                deleteButton.addEventListener('click', () => deleteWatchlist(watchlist));
                listItem.appendChild(deleteButton);

                // Create a span element for the watchlist text
                const watchlistText = document.createElement('span');
                watchlistText.textContent = watchlist;
                listItem.appendChild(document.createTextNode(' ')); // Add a space
                listItem.appendChild(watchlistText);

                watchlistList.appendChild(listItem);

                // Update item notifications for each watchlist
                updateItemNotifications(watchlist);
            });
        })
        .catch(error => console.error('Error updating watchlists:', error));
}

function deleteWatchlist(watchlist) {
    // Send a request to delete the watchlist
    fetch('/delete_watchlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                watchlist
            }),
        })
        .then(response => {
            if (response.ok) {
                console.log(`Watchlist "${watchlist}" deleted successfully.`);
                updateWatchlists(); // Refresh the watchlists after deletion
            } else {
                console.error(`Failed to delete watchlist "${watchlist}".`);
            }
        })
        .catch(error => console.error('Error deleting watchlist:', error));
}

// Update watchlists on page load
updateWatchlists();

// Set an interval to periodically update the watchlists
setInterval(updateWatchlists, 10000); // Update every 10 seconds

//loading bar graphic

function showLoadingBar(event) {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Show the loading bar
    const loaderContainer = document.getElementById('loader-container');
    loaderContainer.style.display = 'block';

    const loaderBar = document.getElementById('loader-bar');
    let width = 0; // Initial width of the loading bar

    function increaseWidth() {
        if (width < 100) {
            width += 1; // Adjust the increment for the desired loading speed
            loaderBar.style.width = `${width}%`;

            // Continue increasing width after a short delay
            setTimeout(increaseWidth, 20); // Adjust the delay for the desired smoothness
        }
    }

    // Start increasing the width
    increaseWidth();

    // Manually trigger the form submission after a short delay
    setTimeout(() => {
        event.target.submit();

        // Hide the loading bar
        loaderContainer.style.display = 'none';
        loaderBar.style.width = '0'; // Reset the width for the next loading
    }, 500);

    // Simulate the data collection process
    fetch('/process_form', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                itemName: event.target.itemName.value,
                zipCode: event.target.zipCode.value,
            }),
        })
        .then(response => {
            if (response.ok) {
                console.log('Request submitted successfully.');
            } else {
                console.error('Failed to submit request.');
            }
        })
        .catch(error => {
            console.error('Error submitting request:', error);
        });
}

// New item notifications

function updateItemNotifications(watchlist) {
    // Fetch item data for the specified watchlist
    fetch(`/get_items?watchlist=${watchlist}`)
        .then(response => response.json())
        .then(data => {
            // Create or get the notification container on the right side
            let notificationContainer = document.getElementById('notificationContainer');

            if (!notificationContainer) {
                // If the container doesn't exist, create it
                notificationContainer = document.createElement('div');
                notificationContainer.id = 'notificationContainer';
                notificationContainer.className = 'split right';
                document.querySelector('.right').appendChild(notificationContainer); // Append to the right side
            }

            console.log(`Received data for ${watchlist}:`, data);

            // Check if data.items is defined and not empty
            if (data.items && data.items.length > 0) {
                // The container exists; proceed to update item notifications
                data.items.forEach(itemData => {
                    // Check if the notification already exists
                    const existingNotification = document.getElementById(`${watchlist}_${itemData.name}_notification`);

                    if (!existingNotification) {
                        // If the notification doesn't exist, create and append it
                        createItemNotification(itemData, watchlist, notificationContainer);
                    }
                });
            } else {
                console.error(`No items data received for ${watchlist}.`);
            }
        })
        .catch(error => console.error(`Error updating item notifications for ${watchlist}:`, error));
}

function createItemNotification(itemData, watchlist, notificationContainer) {
    // Create a container div for the item notification
    const notification = document.createElement('div');
    notification.className = 'notification';

    // Create a delete button for the notification
    const deleteButton = document.createElement('button');
    deleteButton.textContent = 'X';
    deleteButton.addEventListener('click', () => deleteItemNotification(notification, watchlist, itemData.name));
    notification.appendChild(deleteButton);

    // Create a span element for the watchlist text
    const watchlistText = document.createElement('span');
    watchlistText.textContent = watchlist;
    notification.appendChild(document.createTextNode(` New Item Posted for search: ${watchlistText.textContent.split('for ')[1]}`));

    // Create elements for item details
    const itemName = document.createElement('span');
    itemName.textContent = `Item Name: ${itemData.name}`;

    const itemPrice = document.createElement('span');
    itemPrice.textContent = `Item Price: ${itemData.price}`;

    const itemLocation = document.createElement('span');
    itemLocation.textContent = `Item Location: ${itemData.location}`;

    const itemURL = document.createElement('a');
    itemURL.href = itemData.url;
    itemURL.textContent = 'Item URL - Example';

    // Append elements to the notification container
    notification.appendChild(itemName);
    notification.appendChild(itemPrice);
    notification.appendChild(itemLocation);
    notification.appendChild(itemURL);

    // Set a unique ID for the notification
    notification.id = `${watchlist}_${itemData.name}_notification`;

    // Append the notification to the container
    notificationContainer.appendChild(notification);
}

function deleteItemNotification(notification, watchlist, itemName) {
    // Remove the notification from the DOM
    notification.remove();
}

function new_item_alerts(ch, method, properties, body) {
    const messageData = JSON.parse(body);
    const watchlist = messageData.watchlist;

    // Create an item notification for the new item
    updateItemNotifications(watchlist);
}
