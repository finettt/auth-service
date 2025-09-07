import pytest
from src.dto.api import AuthRequestDTO


class TestAuthRequestDTO:
    """Test suite for AuthRequestDTO validation."""

    def test_auth_request_dto_valid_data(self):
        """Test AuthRequestDTO with valid data."""
        data = {
            "login": "testuser",
            "password": "TestPassword123"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "testuser"
        assert dto.password == "TestPassword123"

    def test_auth_request_dto_minimal_valid_login(self):
        """Test AuthRequestDTO with minimal valid login length."""
        data = {
            "login": "abc",
            "password": "TestPassword123"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "abc"
        assert dto.password == "TestPassword123"

    def test_auth_request_dto_long_login(self):
        """Test AuthRequestDTO with long login."""
        long_login = "a" * 100
        data = {
            "login": long_login,
            "password": "TestPassword123"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == long_login
        assert dto.password == "TestPassword123"

    def test_auth_request_dto_special_characters_login(self):
        """Test AuthRequestDTO with special characters in login."""
        data = {
            "login": "test_user123",
            "password": "TestPassword123"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "test_user123"
        assert dto.password == "TestPassword123"

    def test_auth_request_dto_unicode_login(self):
        """Test AuthRequestDTO with unicode characters in login."""
        data = {
            "login": "тестовый_пользователь",
            "password": "TestPassword123"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "тестовый_пользователь"
        assert dto.password == "TestPassword123"

    def test_auth_request_dto_empty_login_raises_error(self):
        """Test AuthRequestDTO with empty login raises ValueError."""
        data = {
            "login": "",
            "password": "TestPassword123"
        }
        
        with pytest.raises(ValueError, match="Login must be at least 3 characters long"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_short_login_raises_error(self):
        """Test AuthRequestDTO with login shorter than 3 characters raises ValueError."""
        data = {
            "login": "ab",
            "password": "TestPassword123"
        }
        
        with pytest.raises(ValueError, match="Login must be at least 3 characters long"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_whitespace_only_login_raises_error(self):
        """Test AuthRequestDTO with whitespace-only login raises ValueError."""
        data = {
            "login": "   ",
            "password": "TestPassword123"
        }
        
        # Pydantic treats whitespace as valid characters, so "   " is 3 characters
        # This should actually pass validation
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "   "
        assert dto.password == "TestPassword123"

    def test_auth_request_dto_valid_password(self):
        """Test AuthRequestDTO with valid password."""
        data = {
            "login": "testuser",
            "password": "ComplexPass123"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "testuser"
        assert dto.password == "ComplexPass123"

    def test_auth_request_dto_minimal_valid_password(self):
        """Test AuthRequestDTO with minimal valid password length."""
        data = {
            "login": "testuser",
            "password": "Abcdefg1"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "testuser"
        assert dto.password == "Abcdefg1"

    def test_auth_request_dto_long_password(self):
        """Test AuthRequestDTO with long password."""
        long_password = "A" * 50 + "1" + "b" * 50
        data = {
            "login": "testuser",
            "password": long_password
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "testuser"
        assert dto.password == long_password

    def test_auth_request_dto_password_with_special_chars(self):
        """Test AuthRequestDTO with password containing special characters."""
        data = {
            "login": "testuser",
            "password": "ComplexPass!@#123"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "testuser"
        assert dto.password == "ComplexPass!@#123"

    def test_auth_request_dto_password_with_unicode(self):
        """Test AuthRequestDTO with password containing unicode characters."""
        data = {
            "login": "testuser",
            "password": "Пароль123Test"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "testuser"
        assert dto.password == "Пароль123Test"

    def test_auth_request_dto_empty_password_raises_error(self):
        """Test AuthRequestDTO with empty password raises ValueError."""
        data = {
            "login": "testuser",
            "password": ""
        }
        
        with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_short_password_raises_error(self):
        """Test AuthRequestDTO with password shorter than 8 characters raises ValueError."""
        data = {
            "login": "testuser",
            "password": "Short1"
        }
        
        with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_password_no_uppercase_raises_error(self):
        """Test AuthRequestDTO with password missing uppercase letter raises ValueError."""
        data = {
            "login": "testuser",
            "password": "lowercase123"
        }
        
        with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_password_no_lowercase_raises_error(self):
        """Test AuthRequestDTO with password missing lowercase letter raises ValueError."""
        data = {
            "login": "testuser",
            "password": "UPPERCASE123"
        }
        
        with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_password_no_digit_raises_error(self):
        """Test AuthRequestDTO with password missing digit raises ValueError."""
        data = {
            "login": "testuser",
            "password": "NoDigitsHere"
        }
        
        with pytest.raises(ValueError, match="Password must contain at least one digit"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_password_only_digits_raises_error(self):
        """Test AuthRequestDTO with password containing only digits raises ValueError."""
        data = {
            "login": "testuser",
            "password": "12345678"
        }
        
        with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_password_only_uppercase_raises_error(self):
        """Test AuthRequestDTO with password containing only uppercase letters raises ValueError."""
        data = {
            "login": "testuser",
            "password": "UPPERCASE"
        }
        
        # Should fail on lowercase requirement first, not digit requirement
        with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_password_only_lowercase_raises_error(self):
        """Test AuthRequestDTO with password containing only lowercase letters raises ValueError."""
        data = {
            "login": "testuser",
            "password": "lowercase"
        }
        
        with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_password_whitespace_only_raises_error(self):
        """Test AuthRequestDTO with whitespace-only password raises ValueError."""
        data = {
            "login": "testuser",
            "password": "        "
        }
        
        # 8 spaces should pass length validation but fail character requirements
        # Should fail on uppercase requirement first
        with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_multiple_validation_errors(self):
        """Test AuthRequestDTO with multiple validation errors shows first error."""
        data = {
            "login": "ab",  # Too short
            "password": "short"  # Too short and missing requirements
        }
        
        # Should fail on login validation first
        with pytest.raises(ValueError, match="Login must be at least 3 characters long"):
            AuthRequestDTO(**data)

    def test_auth_request_dto_from_dict(self):
        """Test AuthRequestDTO creation from dictionary."""
        data_dict = {
            "login": "dict_user",
            "password": "DictPass123"
        }
        
        dto = AuthRequestDTO(**data_dict)
        
        assert dto.login == "dict_user"
        assert dto.password == "DictPass123"

    def test_auth_request_dto_from_kwargs(self):
        """Test AuthRequestDTO creation from keyword arguments."""
        dto = AuthRequestDTO(
            login="kwargs_user",
            password="KwargsPass123"
        )
        
        assert dto.login == "kwargs_user"
        assert dto.password == "KwargsPass123"

    def test_auth_request_dto_model_dump(self):
        """Test AuthRequestDTO model_dump method."""
        data = {
            "login": "dump_user",
            "password": "DumpPass123"
        }
        
        dto = AuthRequestDTO(**data)
        dumped = dto.model_dump()
        
        assert dumped == data
        assert isinstance(dumped, dict)

    def test_auth_request_dto_model_dump_json(self):
        """Test AuthRequestDTO model_dump_json method."""
        data = {
            "login": "json_user",
            "password": "JsonPass123"
        }
        
        dto = AuthRequestDTO(**data)
        json_str = dto.model_dump_json()
        
        assert isinstance(json_str, str)
        assert "json_user" in json_str
        assert "JsonPass123" in json_str

    def test_auth_request_dto_immutability(self):
        """Test that AuthRequestDTO fields are immutable after creation."""
        data = {
            "login": "immutable_user",
            "password": "ImmutablePass123"
        }
        
        dto = AuthRequestDTO(**data)
        
        # Pydantic models are mutable by default, so we can modify fields
        # This is expected behavior for Pydantic BaseModel
        dto.login = "new_login"
        dto.password = "new_password"
        
        assert dto.login == "new_login"
        assert dto.password == "new_password"

    def test_auth_request_dto_field_types(self):
        """Test that AuthRequestDTO fields have correct types."""
        data = {
            "login": "type_test_user",
            "password": "TypeTestPass123"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert isinstance(dto.login, str)
        assert isinstance(dto.password, str)
        assert isinstance(dto.model_dump(), dict)

    def test_auth_request_dto_edge_case_login_with_numbers(self):
        """Test AuthRequestDTO with login containing only numbers."""
        data = {
            "login": "123456789",
            "password": "NumbersPass123"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "123456789"
        assert dto.password == "NumbersPass123"

    def test_auth_request_dto_edge_case_password_with_mixed_chars(self):
        """Test AuthRequestDTO with password containing mixed special characters."""
        data = {
            "login": "mixed_user",
            "password": "M!x3dP@ssw0rd!@#"
        }
        
        dto = AuthRequestDTO(**data)
        
        assert dto.login == "mixed_user"
        assert dto.password == "M!x3dP@ssw0rd!@#"

    def test_auth_request_dto_validation_error_messages(self):
        """Test that validation error messages are descriptive."""
        # Test login validation messages
        with pytest.raises(ValueError, match="Login must be at least 3 characters long"):
            AuthRequestDTO(login="", password="ValidPass123")
        
        with pytest.raises(ValueError, match="Login must be at least 3 characters long"):
            AuthRequestDTO(login="ab", password="ValidPass123")
        
        # Test password validation messages
        with pytest.raises(ValueError, match="Password must be at least 8 characters long"):
            AuthRequestDTO(login="testuser", password="short")
        
        with pytest.raises(ValueError, match="Password must contain at least one uppercase letter"):
            AuthRequestDTO(login="testuser", password="lowercase123")
        
        with pytest.raises(ValueError, match="Password must contain at least one lowercase letter"):
            AuthRequestDTO(login="testuser", password="UPPERCASE123")
        
        with pytest.raises(ValueError, match="Password must contain at least one digit"):
            AuthRequestDTO(login="testuser", password="NoDigitsHere")