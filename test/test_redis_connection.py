import unittest.mock
import pytest
from src.database.redis_connection import get_redis_connection, close_redis_connection


def test_get_redis_connection():
    """Test Redis connection function."""
    # Mock redis.Redis to avoid actual Redis connection
    with unittest.mock.patch("src.database.redis_connection.redis.Redis") as mock_redis:
        mock_conn = unittest.mock.MagicMock()
        mock_redis.return_value = mock_conn
        
        # Call the function
        result = get_redis_connection()
        
        # Verify the result
        assert result == mock_conn
        
        # Verify that Redis was called with expected parameters
        mock_redis.assert_called_once_with(
            host=unittest.mock.ANY,
            port=unittest.mock.ANY,
            db=unittest.mock.ANY,
            decode_responses=True,
        )


def test_close_redis_connection_with_connection():
    """Test closing Redis connection with valid connection."""
    # Create a mock Redis connection
    mock_conn = unittest.mock.MagicMock()
    
    # Call the function
    close_redis_connection(mock_conn)
    
    # Verify that close was called
    mock_conn.close.assert_called_once()


def test_close_redis_connection_with_none():
    """Test closing Redis connection with None."""
    # Call the function with None
    close_redis_connection(None)
    
    # No exception should be raised


def test_close_redis_connection_with_exception():
    """Test closing Redis connection with exception."""
    # Create a mock Redis connection that raises exception on close
    mock_conn = unittest.mock.MagicMock()
    mock_conn.close.side_effect = Exception("Connection already closed")
    
    # Call the function and expect exception
    with pytest.raises(Exception, match="Connection already closed"):
        close_redis_connection(mock_conn)