import unittest.mock
import pytest
import jwt
import datetime
from fastapi.testclient import TestClient
from fastapi import HTTPException, status
from src.app import app
from src.routes.api import get_current_user

client = TestClient(app)


def test_get_current_user_valid_token():
    """Test get_current_user with valid token."""
    # Create a mock token data
    token_data = {
        "sub": "testuser",
        "user_id": 1,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(token_data, "test_secret_key", algorithm="HS256")
    
    # Mock credentials
    mock_credentials = unittest.mock.MagicMock()
    mock_credentials.credentials = token
    
    # Mock TokensDAO
    with unittest.mock.patch("src.routes.api.TokensDAO") as mock_token_dao_class:
        mock_token_dao = unittest.mock.MagicMock()
        mock_token_dao_class.return_value.__enter__.return_value = mock_token_dao
        mock_token_dao.is_token_valid.return_value = True
        
        # Mock settings
        with unittest.mock.patch("src.routes.api.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test_secret_key"
            
            # Call the function
            result = get_current_user(mock_credentials)
            
            # Verify the result
            assert result == {"user_id": 1, "login": "testuser"}


def test_get_current_user_invalid_token_payload():
    """Test get_current_user with invalid token payload."""
    # Create a token with missing user_id
    token_data = {
        "sub": "testuser",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(token_data, "test_secret_key", algorithm="HS256")
    
    # Mock credentials
    mock_credentials = unittest.mock.MagicMock()
    mock_credentials.credentials = token
    
    # Mock settings
    with unittest.mock.patch("src.routes.api.settings") as mock_settings:
        mock_settings.SECRET_KEY = "test_secret_key"
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_credentials)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid token payload"


def test_get_current_user_token_not_in_redis():
    """Test get_current_user with token not found in Redis."""
    # Create a valid token
    token_data = {
        "sub": "testuser",
        "user_id": 1,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(token_data, "test_secret_key", algorithm="HS256")
    
    # Mock credentials
    mock_credentials = unittest.mock.MagicMock()
    mock_credentials.credentials = token
    
    # Mock TokensDAO to return False for is_token_valid
    with unittest.mock.patch("src.routes.api.TokensDAO") as mock_token_dao_class:
        mock_token_dao = unittest.mock.MagicMock()
        mock_token_dao_class.return_value.__enter__.return_value = mock_token_dao
        mock_token_dao.is_token_valid.return_value = False
        
        # Mock settings
        with unittest.mock.patch("src.routes.api.settings") as mock_settings:
            mock_settings.SECRET_KEY = "test_secret_key"
            
            # Call the function and expect exception
            with pytest.raises(HTTPException) as exc_info:
                get_current_user(mock_credentials)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Token not found or expired"


def test_get_current_user_expired_token():
    """Test get_current_user with expired token."""
    # Create an expired token
    token_data = {
        "sub": "testuser",
        "user_id": 1,
        "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1)
    }
    token = jwt.encode(token_data, "test_secret_key", algorithm="HS256")
    
    # Mock credentials
    mock_credentials = unittest.mock.MagicMock()
    mock_credentials.credentials = token
    
    # Mock settings
    with unittest.mock.patch("src.routes.api.settings") as mock_settings:
        mock_settings.SECRET_KEY = "test_secret_key"
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_credentials)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Token has expired"


def test_get_current_user_invalid_token():
    """Test get_current_user with invalid token."""
    # Create an invalid token
    invalid_token = "invalid.token.here"
    
    # Mock credentials
    mock_credentials = unittest.mock.MagicMock()
    mock_credentials.credentials = invalid_token
    
    # Mock settings
    with unittest.mock.patch("src.routes.api.settings") as mock_settings:
        mock_settings.SECRET_KEY = "test_secret_key"
        
        # Call the function and expect exception
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(mock_credentials)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "Invalid token"


def test_logout_account_failure():
    """Test logout account when token deletion fails."""
    with unittest.mock.patch("src.routes.api.TokensDAO") as mock_token_dao_class:
        mock_token_dao = unittest.mock.MagicMock()
        mock_token_dao_class.return_value.__enter__.return_value = mock_token_dao
        mock_token_dao.delete_token.return_value = False
        
        response = client.post("/api/logout", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 400
        assert response.json() == {"detail": "Failed to logout token"}


def test_delete_account_invalid_credentials():
    """Test delete account with invalid credentials."""
    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_dao:
        mock_dao.return_value.__enter__.return_value.get_user_by_login.return_value = None
        response = client.post("/api/delete", json={"login": "testuser", "password": "TestPassword1"})
        assert response.status_code == 401
        assert response.json() == {"message": "Invalid credentials"}


def test_get_profile_user_not_found():
    """Test get profile when user is not found."""
    def mock_get_current_user():
        return {"user_id": 1, "login": "testuser"}

    app.dependency_overrides[get_current_user] = mock_get_current_user

    with unittest.mock.patch("src.routes.api.UsersDAO") as mock_user_dao:
        mock_user_dao.return_value.__enter__.return_value.get_user_by_id.return_value = None
        response = client.get("/api/profile", headers={"Authorization": "Bearer testtoken"})
        assert response.status_code == 404
        assert response.json() == {"detail": "User not found"}

    app.dependency_overrides = {}