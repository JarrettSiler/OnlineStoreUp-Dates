import sys,os
import unittest
from unittest.mock import patch, MagicMock

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
sys.path.append(root_dir)

from applications.data_analyzer_server.src.main.start.App import monitor_directory, check_database, automatic_database_updater


#----------------------------------------------------------------------------------
class AppTestCase(unittest.TestCase):

    def setUp(self):
        pass

    @patch('applications.data_analyzer_server.src.main.start.App.check_database')
    def test_monitor_directory(self, mock_check_database):
        global running
        running = True

        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = ['TEST1.db', 'TEST2.db']
            monitor_directory('directory_path','test')

        self.assertEqual(mock_check_database.call_count, 2)
        mock_check_database.assert_called_with('TEST2')

#----------------------------------------------------------------------------------
        #check to see if all operations are being performed on database
    @patch('applications.data_analyzer_server.src.main.start.App.Database_Handler.is_existing')
    @patch('applications.data_analyzer_server.src.main.start.App.Database_Handler.check_for_new_items')
    @patch('applications.data_analyzer_server.src.main.start.App.send_new_items_to_web')
    @patch('applications.data_analyzer_server.src.main.start.App.os.remove')
    @patch('applications.data_analyzer_server.src.main.start.App.shutil.copy2')
    def test_check_database(self, mock_copy2, mock_remove, mock_send_new_items, mock_check_items, mock_is_existing):
        mock_is_existing.return_value = True
        mock_check_items.return_value = [('item1', '$10.99', 'description', 'newLocation', 'http://example.com')]
        check_database('test_database')

        mock_is_existing.assert_called_once_with('test_database')
        mock_check_items.assert_called_once_with('test_database')
        mock_send_new_items.assert_called_once_with('test_database', 'item1', '$10.99', 'newLocation', 'http://example.com')
        mock_copy2.assert_called_once()
        mock_remove.assert_called_once()

#----------------------------------------------------------------------------------
    #check to see if the automatic updater still operates on a timer
    @patch('applications.data_analyzer_server.src.main.start.App.time.sleep')
    def test_automatic_database_updater(self, mock_sleep):
        global running
        running = True

        automatic_database_updater('directory_to_monitor',1,'test')
        mock_sleep.assert_called_once()

#----------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()