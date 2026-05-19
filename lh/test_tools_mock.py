import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd

# Add the directory to sys.path to import tools
sys.path.append(r"e:\python_workspace\cf\lh")

from tools import Tools

class TestTools(unittest.TestCase):
    @patch('tools.Tools.db_get_mysql_conn')
    def test_db_output(self, mock_get_conn):
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Create a sample DataFrame
        df = pd.DataFrame({
            'Date': ['2023-01-01', '2023-01-02'],
            'Open': [100, 102],
            'Close': [101, 103]
        })
        title = "TestTitle"

        # Mock fetchone for the existence check
        # We have 3 columns.
        # Sequence of calls expected:
        # 1. execute CREATE TABLE ...
        # 2. execute SELECT ... (for col1) -> returns (1,) (id=1)
        # 3. execute UPDATE ...
        # 4. execute SELECT ... (for col2) -> returns None
        # 5. execute INSERT ...
        # 6. execute SELECT ... (for col3) -> returns (2,) (id=2)
        # 7. execute UPDATE ...
        # 8. execute DELETE FROM output ...
        # 9. executemany INSERT INTO output ...
        
        mock_cursor.fetchone.side_effect = [
            (1,), # for col1 exists
            None, # for col2 does not exist
            (2,), # for col3 exists
            # subsequent calls if any (e.g. for delete check if any, but delete uses execute)
        ]

        # Call the method
        Tools.db_output(df, title)

        # Verify calls
        # Check CREATE TABLE
        create_call = mock_cursor.execute.call_args_list[0]
        self.assertIn("CREATE TABLE IF NOT EXISTS `output_column`", create_call[0][0])

        # Check col1 update
        # 2nd execute call should be SELECT for col1
        select_col1 = mock_cursor.execute.call_args_list[1]
        self.assertIn("SELECT `id` FROM `output_column`", select_col1[0][0])
        self.assertEqual(select_col1[0][1], (title, "col1"))
        
        # 3rd execute call should be UPDATE for col1
        update_col1 = mock_cursor.execute.call_args_list[2]
        self.assertIn("UPDATE `output_column`", update_col1[0][0])
        self.assertEqual(update_col1[0][1], ("Date", 1))

        # Check col2 insert
        # 4th execute call should be SELECT for col2
        select_col2 = mock_cursor.execute.call_args_list[3]
        self.assertIn("SELECT `id` FROM `output_column`", select_col2[0][0])
        self.assertEqual(select_col2[0][1], (title, "col2"))
        
        # 5th execute call should be INSERT for col2
        insert_col2 = mock_cursor.execute.call_args_list[4]
        self.assertIn("INSERT INTO `output_column`", insert_col2[0][0])
        self.assertEqual(insert_col2[0][1], (title, "col2", "Open"))

        # Check output table delete
        # calls so far: create, sel1, upd1, sel2, ins2, sel3, upd3.
        # Next is delete.
        # 1 + 2 + 2 + 2 = 7 calls related to columns.
        # So 8th call (index 7) should be DELETE
        delete_call = mock_cursor.execute.call_args_list[7]
        self.assertIn("DELETE FROM `output`", delete_call[0][0])
        
        # Check output table insert (executemany)
        self.assertTrue(mock_cursor.executemany.called)
        args, _ = mock_cursor.executemany.call_args
        self.assertIn("INSERT INTO `output`", args[0])
        self.assertEqual(len(args[1]), 2) # 2 rows in DF
        
        print("Test passed!")

if __name__ == '__main__':
    unittest.main()
