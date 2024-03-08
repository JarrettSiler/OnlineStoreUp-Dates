import sys,os
import unittest
from unittest.mock import patch, Mock, MagicMock
from sqlalchemy import MetaData

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "..", ".."))
sys.path.append(root_dir)
from applications.data_collector_server.src.main.start.App import truncate_db, collect_data, process_message
from applications.data_collector_server.src.main.start import App



#----------------------------------------------------------------------------------
class TestYourScript(unittest.TestCase):

#----------------------------------------------------------------------------------

    @patch('applications.data_collector_server.src.main.start.App.MetaData')
    def test_truncate_db(self, mock_metadata):
        mock_engine = MagicMock()
        mock_con = mock_engine.connect.return_value
        mock_table1 = Mock()
        mock_table2 = Mock()

        mock_metadata.return_value.reflect.return_value = [mock_table1, mock_table2]

        # Assuming Base is defined in App module
        with patch('applications.data_collector_server.src.main.start.App.Base'):
            App.Base.metadata.sorted_tables = [mock_table1, mock_table2]
            truncate_db(mock_engine)

        mock_metadata.assert_called_once_with()
        mock_engine.connect.assert_called_once()
        mock_con.begin.assert_called_once()

        # Check if the delete method of the mock tables is called once for each table
        mock_table1.delete_called_once()
        mock_table2.delete_called_once()

#----------------------------------------------------------------------------------
    def test_src_directory_legitimate(self):
        src = os.path.join(root_dir, 'database_storage', 'Temporary', 'tmp.db')
        self.assertTrue(os.path.isdir(os.path.dirname(src)), f"Source directory {os.path.dirname(src)} is not a valid directory.")

    def test_dst_directory_legitimate(self):
        item = 'TestItem'
        zc = '12345'
        dst = os.path.join(root_dir, 'database_storage', 'To Be Analyzed', f"{item.replace(' ', '_')}_{zc}.db")
        self.assertTrue(os.path.isdir(os.path.dirname(dst)), f"Destination directory {os.path.dirname(dst)} is not a valid directory.")

#----------------------------------------------------------------------------------
    @patch('applications.data_collector_server.src.main.start.App.json.loads')
    @patch('applications.data_collector_server.src.main.start.App.collect_data')
    def test_process_message(self, mock_collect_data, mock_json_loads):
        mock_body = Mock()
        mock_data = {'itemname': 'TestItem', 'zipcode': '12345'}
        mock_json_loads.return_value = mock_data

        process_message(mock_body)

        mock_json_loads.assert_called_once_with(mock_body)

#----------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
