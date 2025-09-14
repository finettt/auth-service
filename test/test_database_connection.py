import pytest
import psycopg
import os
from unittest.mock import patch
from dotenv import load_dotenv

from src.database.connection import get_db_connection, DATABASE_URL

load_dotenv()


class TestDatabaseConnection:
    """Test suite for database connection functions."""

    def test_get_db_connection_returns_connection(self):
        """Test that get_db_connection returns a valid connection object."""
        conn = get_db_connection()

        # Verify it's a psycopg connection
        assert isinstance(conn, psycopg.Connection)

        # Clean up
        conn.close()

    def test_get_db_connection_with_custom_url(self):
        """Test database connection with custom database URL."""
        test_url = "postgresql://test:test@localhost:5432/testdb"

        with patch("src.database.connection.DATABASE_URL", test_url):
            conn = get_db_connection()

            # Verify it's a valid connection
            assert isinstance(conn, psycopg.Connection)

            # Test basic query
            result = conn.execute("SELECT 1").fetchone()
            assert result is not None
            assert result[0] == 1

            conn.close()

    def test_get_db_connection_default_url(self):
        """Test that default database URL is used when no environment variable is set."""
        with patch.dict(os.environ, {}, clear=True):
            # Temporarily patch the DATABASE_URL to check default behavior
            with patch(
                "src.database.connection.DATABASE_URL",
                "postgresql://postgres:postgres@localhost:5432/auth",
            ):
                conn = get_db_connection()

                # Verify it's a valid connection
                assert isinstance(conn, psycopg.Connection)

                # Test basic query
                result = conn.execute("SELECT 1").fetchone()
                assert result is not None
                assert result[0] == 1

                conn.close()

    def test_get_db_connection_with_env_var(self):
        """Test database connection with DATABASE_URL environment variable."""
        test_url = "postgresql://env:env@localhost:5432/envdb"

        with patch.dict(os.environ, {"DATABASE_URL": test_url}):
            # Force reload of the module to pick up the environment variable
            import importlib
            import src.database.connection

            importlib.reload(src.database.connection)

            conn = src.database.connection.get_db_connection()

            # Verify it's a valid connection
            assert isinstance(conn, psycopg.Connection)

            # Test basic query
            result = conn.execute("SELECT 1").fetchone()
            assert result is not None
            assert result[0] == 1

            conn.close()

    def test_get_db_connection_multiple_calls(self):
        """Test that multiple calls to get_db_connection return separate connections."""
        conn1 = get_db_connection()
        conn2 = get_db_connection()

        # Verify they are different connection objects
        assert conn1 is not conn2

        # Both should be valid connections
        assert isinstance(conn1, psycopg.Connection)
        assert isinstance(conn2, psycopg.Connection)

        # Clean up
        conn1.close()
        conn2.close()

    def test_get_db_connection_error_handling(self):
        """Test error handling when database URL is invalid."""
        invalid_url = "postgresql://invalid:invalid@nonexistent:5432/auth"

        # Test with invalid database URL
        with patch("src.database.connection.DATABASE_URL", invalid_url):
            with pytest.raises(Exception):  # psycopg will raise a connection error
                get_db_connection()

    def test_database_url_constant(self):
        """Test that DATABASE_URL constant is properly defined."""
        assert isinstance(DATABASE_URL, str)
        assert len(DATABASE_URL) > 0
        assert DATABASE_URL.startswith("postgresql://")

    def test_get_db_connection_can_execute_queries(self):
        """Test that connection can execute basic queries."""
        conn = get_db_connection()

        try:
            # Test basic query
            result = conn.execute("SELECT 1 as test_value").fetchone()
            assert result is not None
            assert result[0] == 1

            # Test parameterized query
            result = conn.execute("SELECT %s as test_value", (42,)).fetchone()
            assert result is not None
            assert result[0] == 42

        finally:
            conn.close()

    def test_get_db_connection_transaction_handling(self):
        """Test that connection handles transactions properly."""
        conn = get_db_connection()

        try:
            # Start a transaction
            with conn.transaction():
                # Execute a query within transaction
                result = conn.execute("SELECT 1").fetchone()
                assert result is not None
                assert result[0] == 1

        finally:
            conn.close()
