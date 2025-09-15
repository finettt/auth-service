import unittest.mock
import json
from datetime import datetime, timedelta
from src.database.dao.tokens import TokensDAO


def test_tokens_dao_init():
    """Test TokensDAO initialization."""
    dao = TokensDAO()
    assert dao.redis_conn is None


def test_tokens_dao_context_manager():
    """Test TokensDAO context manager functionality."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            assert dao.redis_conn == mock_conn
        
        # Verify that close was called
        mock_conn.close.assert_called_once()


def test_store_token_success():
    """Test store_token method success case."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.store_token(1, "test_token")
            
            assert result is True
            mock_conn.setex.assert_called_once()


def test_store_token_with_custom_expires():
    """Test store_token method with custom expiration."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.store_token(1, "test_token", expires_in_hours=12)
            
            assert result is True
            # Check that setex was called with 12 hours in seconds
            args, kwargs = mock_conn.setex.call_args
            assert args[1] == 12 * 3600


def test_store_token_exception():
    """Test store_token method with exception."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.setex.side_effect = Exception("Redis error")
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.store_token(1, "test_token")
            
            assert result is False


def test_get_token_success():
    """Test get_token method success case."""
    token_data = {
        "user_id": 1,
        "expires_at": "2023-12-31T23:59:59",
        "created_at": "2023-01-01T00:00:00"
    }
    
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.get.return_value = json.dumps(token_data)
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.get_token("test_token")
            
            assert result == token_data
            mock_conn.get.assert_called_once_with("token:test_token")


def test_get_token_not_found():
    """Test get_token method when token is not found."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.get.return_value = None
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.get_token("nonexistent_token")
            
            assert result is None


def test_get_token_exception():
    """Test get_token method with exception."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.get.side_effect = Exception("Redis error")
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.get_token("test_token")
            
            assert result is None


def test_delete_token_success():
    """Test delete_token method success case."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.delete.return_value = 1
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.delete_token("test_token")
            
            assert result is True
            mock_conn.delete.assert_called_once_with("token:test_token")


def test_delete_token_not_found():
    """Test delete_token method when token is not found."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.delete.return_value = 0
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.delete_token("nonexistent_token")
            
            assert result is False


def test_delete_token_exception():
    """Test delete_token method with exception."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.delete.side_effect = Exception("Redis error")
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.delete_token("test_token")
            
            assert result is False


def test_is_token_valid_valid():
    """Test is_token_valid method with valid token."""
    future_time = (datetime.now() + timedelta(hours=1)).isoformat()
    token_data = {
        "user_id": 1,
        "expires_at": future_time,
        "created_at": "2023-01-01T00:00:00"
    }
    
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            with unittest.mock.patch.object(dao, "get_token", return_value=token_data):
                result = dao.is_token_valid("test_token")
                
                assert result is True


def test_is_token_valid_expired():
    """Test is_token_valid method with expired token."""
    past_time = (datetime.now() - timedelta(hours=1)).isoformat()
    token_data = {
        "user_id": 1,
        "expires_at": past_time,
        "created_at": "2023-01-01T00:00:00"
    }
    
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            with unittest.mock.patch.object(dao, "get_token", return_value=token_data):
                result = dao.is_token_valid("test_token")
                
                assert result is False


def test_is_token_valid_not_found():
    """Test is_token_valid method when token is not found."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            with unittest.mock.patch.object(dao, "get_token", return_value=None):
                result = dao.is_token_valid("nonexistent_token")
                
                assert result is False


def test_is_token_valid_exception():
    """Test is_token_valid method with exception."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            with unittest.mock.patch.object(dao, "get_token", side_effect=Exception("Redis error")):
                result = dao.is_token_valid("test_token")
                
                assert result is False


def test_get_user_tokens_success():
    """Test get_user_tokens method success case."""
    token_data1 = {
        "user_id": 1,
        "expires_at": "2023-12-31T23:59:59",
        "created_at": "2023-01-01T00:00:00"
    }
    token_data2 = {
        "user_id": 2,
        "expires_at": "2023-12-31T23:59:59",
        "created_at": "2023-01-01T00:00:00"
    }
    
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.keys.return_value = ["token:test_token1", "token:test_token2"]
        mock_conn.get.side_effect = [json.dumps(token_data1), json.dumps(token_data2)]
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.get_user_tokens(1)
            
            assert len(result) == 1
            assert result[0]["token"] == "test_token1"
            assert result[0]["expires_at"] == "2023-12-31T23:59:59"
            assert result[0]["created_at"] == "2023-01-01T00:00:00"


def test_get_user_tokens_no_tokens():
    """Test get_user_tokens method when no tokens exist."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.keys.return_value = []
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.get_user_tokens(1)
            
            assert result == []


def test_get_user_tokens_exception():
    """Test get_user_tokens method with exception."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.keys.side_effect = Exception("Redis error")
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.get_user_tokens(1)
            
            assert result == []


def test_revoke_user_tokens_success():
    """Test revoke_user_tokens method success case."""
    token_data1 = {
        "user_id": 1,
        "expires_at": "2023-12-31T23:59:59",
        "created_at": "2023-01-01T00:00:00"
    }
    token_data2 = {
        "user_id": 2,
        "expires_at": "2023-12-31T23:59:59",
        "created_at": "2023-01-01T00:00:00"
    }
    
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.keys.return_value = ["token:test_token1", "token:test_token2"]
        mock_conn.get.side_effect = [json.dumps(token_data1), json.dumps(token_data2)]
        mock_conn.delete.return_value = 1
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.revoke_user_tokens(1)
            
            assert result == 1
            assert mock_conn.delete.call_count == 1


def test_revoke_user_tokens_no_tokens():
    """Test revoke_user_tokens method when no tokens exist."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.keys.return_value = []
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.revoke_user_tokens(1)
            
            assert result == 0


def test_revoke_user_tokens_exception():
    """Test revoke_user_tokens method with exception."""
    with unittest.mock.patch("src.database.dao.tokens.get_redis_connection") as mock_get_conn:
        mock_conn = unittest.mock.MagicMock()
        mock_conn.keys.side_effect = Exception("Redis error")
        mock_get_conn.return_value = mock_conn
        
        with TokensDAO() as dao:
            result = dao.revoke_user_tokens(1)
            
            assert result == 0