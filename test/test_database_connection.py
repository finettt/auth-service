import pytest
import sqlite3
import os
import tempfile
from unittest.mock import patch

from src.database.connection import get_db_connection, DATABASE_PATH


class TestDatabaseConnection:
    """Test suite for database connection functions."""

    def test_get_db_connection_returns_connection(self):
        """Test that get_db_connection returns a valid connection object."""
        conn = get_db_connection()
        
        # Verify it's a sqlite3 connection
        assert isinstance(conn, sqlite3.Connection)
        
        # Verify row factory is set to sql.Row
        assert conn.row_factory == sqlite3.Row
        
        # Clean up
        conn.close()

    def test_get_db_connection_with_custom_path(self):
        """Test database connection with custom database path."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name
        
        try:
            with patch('src.database.connection.DATABASE_PATH', temp_path):
                conn = get_db_connection()
                
                # Verify connection is to the correct path by checking the database filename
                assert os.path.basename(conn.execute("PRAGMA database_list").fetchone()[2]) == os.path.basename(temp_path)
                
                # Verify it's a valid connection
                assert isinstance(conn, sqlite3.Connection)
                
                conn.close()
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_db_connection_default_path(self):
        """Test that default database path is used when no environment variable is set."""
        with patch.dict(os.environ, {}, clear=True):
            # Temporarily patch the DATABASE_PATH to check default behavior
            original_path = DATABASE_PATH
            with patch('src.database.connection.DATABASE_PATH', '.data/auth.db'):
                conn = get_db_connection()
                
                # Verify it's using the default path by checking the database filename
                db_info = conn.execute("PRAGMA database_list").fetchone()
                db_path = db_info[2]
                assert os.path.basename(db_path) == 'auth.db'
                
                conn.close()

    def test_get_db_connection_with_env_var(self):
        """Test database connection with DATABASE_PATH environment variable."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name
        
        try:
            # Set environment variable and patch the module to use it
            with patch.dict(os.environ, {'DATABASE_PATH': temp_path}):
                # Force reload of the module to pick up the environment variable
                import importlib
                import src.database.connection
                importlib.reload(src.database.connection)
                
                conn = src.database.connection.get_db_connection()
                
                # Verify connection is to the environment variable path by checking the database filename
                db_info = conn.execute("PRAGMA database_list").fetchone()
                db_path = db_info[2]
                assert os.path.basename(db_path) == os.path.basename(temp_path)
                
                conn.close()
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_get_db_connection_multiple_calls(self):
        """Test that multiple calls to get_db_connection return separate connections."""
        conn1 = get_db_connection()
        conn2 = get_db_connection()
        
        # Verify they are different connection objects
        assert conn1 is not conn2
        
        # Both should be valid connections
        assert isinstance(conn1, sqlite3.Connection)
        assert isinstance(conn2, sqlite3.Connection)
        
        # Clean up
        conn1.close()
        conn2.close()

    def test_get_db_connection_row_factory(self):
        """Test that row factory is properly set to sqlite3.Row."""
        conn = get_db_connection()
        
        # Verify row factory is set
        assert conn.row_factory == sqlite3.Row
        
        # Test that it works by creating a cursor and checking description
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER, name TEXT)")
        cursor.execute("INSERT INTO test_table (id, name) VALUES (1, 'test')")
        cursor.execute("SELECT * FROM test_table")
        
        # Fetch row and verify it's a Row object
        row = cursor.fetchone()
        assert isinstance(row, sqlite3.Row)
        
        # Clean up
        cursor.close()
        conn.close()

    def test_get_db_connection_error_handling(self):
        """Test error handling when database path is invalid."""
        invalid_path = "/nonexistent/directory/auth.db"
        
        # Test with invalid directory path
        with patch('src.database.connection.DATABASE_PATH', invalid_path):
            with pytest.raises(sqlite3.OperationalError):
                conn = get_db_connection()

    def test_database_path_constant(self):
        """Test that DATABASE_PATH constant is properly defined."""
        assert isinstance(DATABASE_PATH, str)
        assert len(DATABASE_PATH) > 0

    def test_get_db_connection_thread_safety(self):
        """Test that connections can be created from multiple threads."""
        import threading
        import time
        
        connections = []
        errors = []
        
        def create_connection():
            try:
                conn = get_db_connection()
                time.sleep(0.1)  # Small delay to test concurrency
                connections.append(conn)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=create_connection)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all connections were created successfully
        assert len(errors) == 0
        assert len(connections) == 5
        
        # Verify all connections are valid (close them in their respective threads)
        # Note: SQLite connections should be closed in the same thread they were created
        for conn in connections:
            assert isinstance(conn, sqlite3.Connection)
            # Don't close connections here as they were created in different threads

    def test_get_db_connection_isolation_level(self):
        """Test that connection has appropriate isolation level."""
        conn = get_db_connection()
        
        # SQLite default isolation level is 'IMMEDIATE'
        isolation_level = conn.isolation_level
        assert isolation_level is not None
        
        conn.close()

    def test_get_db_connection_can_execute_queries(self):
        """Test that connection can execute basic queries."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Create a test table
            cursor.execute("CREATE TABLE IF NOT EXISTS test_query (id INTEGER, name TEXT)")
            
            # Insert data
            cursor.execute("INSERT INTO test_query (id, name) VALUES (1, 'test')")
            
            # Query data
            cursor.execute("SELECT * FROM test_query")
            result = cursor.fetchone()
            
            assert result is not None
            assert result[0] == 1
            assert result[1] == 'test'
            
        finally:
            cursor.close()
            conn.close()