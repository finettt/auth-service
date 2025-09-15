import pytest
from src.dto.api import AuthRequestDTO


def test_auth_request_dto_valid():
    """Test AuthRequestDTO with valid data."""
    data = {
        "login": "testuser",
        "password": "TestPassword123"
    }
    
    dto = AuthRequestDTO(**data)
    
    assert dto.login == "testuser"
    assert dto.password == "TestPassword123"


def test_auth_request_dto_login_too_short():
    """Test AuthRequestDTO with login that is too short."""
    data = {
        "login": "ab",  # Less than 3 characters
        "password": "TestPassword123"
    }
    
    with pytest.raises(ValueError, match="Login must be at least 3 characters long"):
        AuthRequestDTO(**data)


def test_auth_request_dto_login_empty():
    """Test AuthRequestDTO with empty login."""
    data = {
        "login": "",  # Empty login
        "password": "TestPassword123"
    }
    
    with pytest.raises(ValueError, match="Login must be at least 3 characters long"):
        AuthRequestDTO(**data)


def test_auth_request_dto_password_too_short():
    """Test AuthRequestDTO with password that is too short."""
    data = {
        "login": "testuser",
        "password": "Short1"  # Less than 8 characters
    }
    
    with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
        AuthRequestDTO(**data)


def test_auth_request_dto_password_no_uppercase():
    """Test AuthRequestDTO with password without uppercase letter."""
    data = {
        "login": "testuser",
        "password": "testpassword123"  # No uppercase letter
    }
    
    with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
        AuthRequestDTO(**data)


def test_auth_request_dto_password_no_lowercase():
    """Test AuthRequestDTO with password without lowercase letter."""
    data = {
        "login": "testuser",
        "password": "TESTPASSWORD123"  # No lowercase letter
    }
    
    with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
        AuthRequestDTO(**data)


def test_auth_request_dto_password_no_digit():
    """Test AuthRequestDTO with password without digit."""
    data = {
        "login": "testuser",
        "password": "TestPassword"  # No digit
    }
    
    with pytest.raises(ValueError, match="Password must contain at least one digit"):
        AuthRequestDTO(**data)


def test_auth_request_dto_password_empty():
    """Test AuthRequestDTO with empty password."""
    data = {
        "login": "testuser",
        "password": ""  # Empty password
    }
    
    with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
        AuthRequestDTO(**data)


def test_auth_request_dto_multiple_validation_errors():
    """Test AuthRequestDTO with multiple validation errors."""
    data = {
        "login": "ab",  # Too short
        "password": "short"  # Too short, no uppercase, no digit
    }
    
    # Should fail on first validation error (login length)
    with pytest.raises(ValueError, match="Login must be at least 3 characters long"):
        AuthRequestDTO(**data)