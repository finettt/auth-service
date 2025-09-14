from datetime import datetime
from src.database.dao.tokens import TokensDAO
from src.database.redis_connection import get_redis_connection


class TestTokensRedis:
    """Test cases for Redis token management."""

    def setup_method(self):
        """Set up test environment."""
        self.redis_conn = get_redis_connection()
        # Clear any existing test data
        self.redis_conn.flushdb()

    def teardown_method(self):
        """Clean up test environment."""
        if self.redis_conn:
            self.redis_conn.flushdb()
            self.redis_conn.close()

    def test_store_and_retrieve_token(self):
        """Test storing and retrieving a token."""
        user_id = 1
        token = "test_token_123"

        with TokensDAO() as token_dao:
            # Store token
            result = token_dao.store_token(user_id, token, expires_in_hours=1)
            assert result is True

            # Retrieve token
            retrieved_data = token_dao.get_token(token)
            assert retrieved_data is not None
            assert retrieved_data["user_id"] == user_id
            assert "expires_at" in retrieved_data
            assert "created_at" in retrieved_data

    def test_token_expiration(self):
        """Test token expiration functionality."""
        user_id = 2
        token = "expired_token_456"

        with TokensDAO() as token_dao:
            # Store token with very short expiration
            token_dao.store_token(
                user_id, token, expires_in_hours=0.001
            )  # ~3.6 seconds

            # Token should be valid immediately
            assert token_dao.is_token_valid(token) is True

            # Wait for expiration and check again
            import time

            time.sleep(1)  # Wait a bit longer than the expiration

            # Token should now be expired
            assert token_dao.is_token_valid(token) is False

    def test_delete_token(self):
        """Test deleting a token."""
        user_id = 3
        token = "delete_token_789"

        with TokensDAO() as token_dao:
            # Store token
            token_dao.store_token(user_id, token)

            # Verify token exists
            assert token_dao.get_token(token) is not None

            # Delete token
            result = token_dao.delete_token(token)
            assert result is True

            # Verify token is deleted
            assert token_dao.get_token(token) is None

    def test_get_user_tokens(self):
        """Test getting all tokens for a specific user."""
        user_id = 4
        tokens = [f"user_token_{i}" for i in range(3)]

        with TokensDAO() as token_dao:
            # Store multiple tokens for the same user
            for token in tokens:
                token_dao.store_token(user_id, token)

            # Store a token for a different user
            token_dao.store_token(999, "other_user_token")

            # Get tokens for the user
            user_tokens = token_dao.get_user_tokens(user_id)
            assert len(user_tokens) == 3

            # Verify all tokens belong to the user
            for token_info in user_tokens:
                assert token_info["user_id"] == user_id
                assert token_info["token"] in tokens

    def test_revoke_user_tokens(self):
        """Test revoking all tokens for a user."""
        user_id = 5
        tokens = [f"revoke_token_{i}" for i in range(2)]

        with TokensDAO() as token_dao:
            # Store tokens for the user
            for token in tokens:
                token_dao.store_token(user_id, token)

            # Store a token for a different user
            token_dao.store_token(888, "other_token")

            # Revoke user tokens
            revoked_count = token_dao.revoke_user_tokens(user_id)
            assert revoked_count == 2

            # Verify user tokens are revoked
            user_tokens = token_dao.get_user_tokens(user_id)
            assert len(user_tokens) == 0

            # Verify other user's token still exists
            assert token_dao.get_token("other_token") is not None

    def test_invalid_token_operations(self):
        """Test operations with invalid/non-existent tokens."""
        with TokensDAO() as token_dao:
            # Get non-existent token
            assert token_dao.get_token("non_existent_token") is None

            # Delete non-existent token
            assert token_dao.delete_token("non_existent_token") is False

            # Check validity of non-existent token
            assert token_dao.is_token_valid("non_existent_token") is False

    def test_token_data_structure(self):
        """Test that token data is properly structured."""
        user_id = 6
        token = "structure_test_token"

        with TokensDAO() as token_dao:
            token_dao.store_token(user_id, token)
            token_data = token_dao.get_token(token)

            # Verify data structure
            assert isinstance(token_data, dict)
            assert "user_id" in token_data
            assert "expires_at" in token_data
            assert "created_at" in token_data

            # Verify data types
            assert isinstance(token_data["user_id"], int)
            assert isinstance(token_data["expires_at"], str)
            assert isinstance(token_data["created_at"], str)

            # Verify timestamps are valid ISO format
            datetime.fromisoformat(token_data["expires_at"])
            datetime.fromisoformat(token_data["created_at"])
