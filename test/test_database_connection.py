import unittest.mock
import pytest
from src.database.connection import get_db_connection, DATABASE_URL


def test_database_url_format():
    """Test that DATABASE_URL is properly formatted."""
    # Check that DATABASE_URL contains expected components
    assert "://" in DATABASE_URL
    assert "@" in DATABASE_URL
    assert ":" in DATABASE_URL.split("@")[0]  # user:password part
    assert ":" in DATABASE_URL.split("@")[1]  # host:port part


def test_get_db_connection():
    """Test database connection function."""
    # Mock psycopg.connect to avoid actual database connection
    with unittest.mock.patch("src.database.connection.psycopg.connect") as mock_connect:
        mock_conn = unittest.mock.MagicMock()
        mock_connect.return_value = mock_conn
        
        # Call the function
        result = get_db_connection()
        
        # Verify the result
        assert result == mock_conn
        
        # Verify that connect was called with DATABASE_URL
        mock_connect.assert_called_once_with(DATABASE_URL)


def test_get_db_connection_exception():
    """Test database connection function with exception."""
    # Mock psycopg.connect to raise an exception
    with unittest.mock.patch("src.database.connection.psycopg.connect") as mock_connect:
        mock_connect.side_effect = Exception("Connection failed")
        
        # Call the function and expect exception
        with pytest.raises(Exception, match="Connection failed"):
            get_db_connection()