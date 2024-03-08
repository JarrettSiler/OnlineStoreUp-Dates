import sys
import os
import unittest
from unittest.mock import patch, MagicMock

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
sys.path.append(root_dir)

from applications.basic_server.src.main.start.App import app

#----------------------------------------------------------------------------------
class AppTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

#----------------------------------------------------------------------------------
    def test_access_home_page(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

#----------------------------------------------------------------------------------
    def test_delete_watchlist(self):

        # Simulate deleting the watchlist
        response = self.app.post('/delete_watchlist', json=dict(
            watchlist='Watch set for TestItem in 12345'
        ), content_type='application/json', follow_redirects=True)

        # Assert that the watchlist is deleted successfully
        self.assertNotIn(b'TestItem', response.data)
        self.assertNotIn(b'12345', response.data)

#----------------------------------------------------------------------------------
    def add_new_item_alert(self):
        # Simulate receiving a new item alert
        response = self.app.post('/get_items', json={
            'watchlist': 'Watch set for TestItem in 12345',
            'name': 'NewItem',
            'price': '$99.99',
            'location': 'NewLocation',
            'url': 'http://example.com'
        }, content_type='application/json')

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)

#----------------------------------------------------------------------------------
    def test_delete_item_notification(self):
        # Simulate deleting an item notification
        response = self.app.post('/delete_item', json={
            'watchlist': 'Watch set for TestItem in 12345',
            'name': 'NewItem',
            'price': '$99.99',
            'location': 'NewLocation',
            'url': 'http://example.com'
        }, content_type='application/json')

        # Assert that the response is as expected
        self.assertEqual(response.status_code, 200)

        # Assert that the item notification is deleted successfully
        self.assertNotIn(b'NewItem', response.data)
        self.assertNotIn(b'$99.99', response.data)
        self.assertNotIn(b'NewLocation', response.data)

if __name__ == '__main__':
    unittest.main()