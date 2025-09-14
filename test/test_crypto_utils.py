import pytest
from src.crypto.utils import encrypt_password, verify_password


def test_encrypt_password():
    """Test password encryption function."""
    password = "TestPassword123"
    hashed = encrypt_password(password)
    
    # Check that the hash is a string
    assert isinstance(hashed, str)
    
    # Check that the hash is not the same as the password
    assert hashed != password
    
    # Check that the hash contains bcrypt format
    assert "$2b$" in hashed


def test_verify_password_correct():
    """Test password verification with correct password."""
    password = "TestPassword123"
    hashed = encrypt_password(password)
    
    # Check that correct password verifies successfully
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """Test password verification with incorrect password."""
    password = "TestPassword123"
    wrong_password = "WrongPassword123"
    hashed = encrypt_password(password)
    
    # Check that incorrect password fails verification
    assert verify_password(wrong_password, hashed) is False


def test_verify_password_empty():
    """Test password verification with empty password."""
    password = "TestPassword123"
    empty_password = ""
    hashed = encrypt_password(password)
    
    # Check that empty password fails verification
    assert verify_password(empty_password, hashed) is False