import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import sys
import os

# Add parent directory to path to allow direct script execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the database manager before it's imported by the app
db_manager_mock = MagicMock()

def setUpModule():
    """Set up the patcher once for the entire module."""
    global patcher
    # Patch the db_manager object *within the app module* where it is used.
    patcher = patch('app.db_manager', db_manager_mock)
    patcher.start()

def tearDownModule():
    """Tear down the patcher once after all tests are done."""
    patcher.stop()

# Import the app and other necessary components after patching
from app import update_main_content

class TestDataRetrieval(unittest.TestCase):

    def setUp(self):
        """Reset the mock before each test."""
        db_manager_mock.reset_mock()
        # Reset side_effect if it was set in a previous test
        db_manager_mock.get_data_for_keyword.side_effect = None

    def test_successful_data_retrieval(self):
        """
        Test if data is retrieved and processed correctly when `get_data_for_keyword` returns valid data.
        """
        # Configure the mock to return a sample dataset
        sample_datasets_norm = {
            'GT': pd.DataFrame({'Value': [10, 20]}, index=pd.to_datetime(['2023-01-01', '2023-02-01'])),
            'CR': pd.DataFrame({'Value': [30, 40]}, index=pd.to_datetime(['2023-01-01', '2023-02-01']))
        }
        db_manager_mock.get_data_for_keyword.return_value = (sample_datasets_norm, ['GT', 'CR'])

        selected_keyword = "Some Tool"
        selected_sources_display = ["Google Trends", "Crossref.org"]

        # Call the callback function
        main_content, credits_open = update_main_content(selected_sources_display, selected_keyword)

        # Verify credits are collapsed and content is generated
        self.assertFalse(credits_open)
        # Check that the main content is a Dash Div component
        from dash import html
        self.assertIsInstance(main_content, html.Div)
        # Ensure the div is not rendering placeholder text
        self.assertNotIn("Por favor, seleccione una Herramienta", main_content.children)
        # Ensure the div is not rendering the 'no data' message
        self.assertNotIn("No hay datos disponibles", str(main_content.children))
        # Check if the returned content has children (the graphs and tables)
        self.assertTrue(len(main_content.children) > 0)

    def test_no_data_retrieved(self):
        """
        Test the behavior when `get_data_for_keyword` returns no data.
        """
        # Configure the mock to return an empty dataset
        db_manager_mock.get_data_for_keyword.return_value = ({}, [])
        
        selected_keyword = "Another Tool"
        selected_sources_display = ["Google Trends"]

        # Call the callback function
        main_content, credits_open = update_main_content(selected_sources_display, selected_keyword)
        
        # Verify credits are collapsed and the "no data" message is shown
        self.assertFalse(credits_open)
        self.assertIn(f"No hay datos disponibles para la herramienta '{selected_keyword}'", main_content.children)

    def test_database_exception(self):
        """
        Test the behavior when `get_data_for_keyword` raises an exception.
        """
        # Configure the mock to raise an exception
        error_message = "Database connection failed"
        db_manager_mock.get_data_for_keyword.side_effect = Exception(error_message)
        
        selected_keyword = "Failing Tool"
        selected_sources_display = ["Bain - Usabilidad"]

        # Call the callback function
        main_content, credits_open = update_main_content(selected_sources_display, selected_keyword)
        
        # Verify the generic error message is displayed
        self.assertFalse(credits_open)
        self.assertIn(f"Error: {error_message}", main_content.children)

    def test_no_keyword_or_sources_selected(self):
        """
        Test the initial state when no keyword or sources are selected.
        """
        # Test with no keyword
        main_content, credits_open = update_main_content(["Google Trends"], None)
        self.assertTrue(credits_open)
        self.assertIn("Por favor, seleccione una Herramienta", main_content.children)
        
        # Test with no sources
        main_content, credits_open = update_main_content([], "Some Tool")
        self.assertTrue(credits_open)
        self.assertIn("Por favor, seleccione una Herramienta", main_content.children)

if __name__ == '__main__':
    unittest.main()