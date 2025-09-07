import pytest
import sqlite3
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import patch

from src.database.connection import get_db_connection


class TestDatabaseSetup:
    """Test suite for database initialization and setup."""

    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database path for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
            temp_path = temp_db.name
        
        yield temp_path
        
        # Clean up
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_database_creation_on_first_connection(self):
        """Test that database file is created on first connection."""
        # Create a temporary directory for the database
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'test.db')
        
        try:
            # Ensure database doesn't exist initially
            assert not os.path.exists(temp_path)
            
            # Connect to database (should create it)
            with patch('src.database.connection.DATABASE_PATH', temp_path):
                conn = get_db_connection()
                
                # Verify database file was created
                assert os.path.exists(temp_path)
                
                # Verify it's a valid SQLite database
                assert isinstance(conn, sqlite3.Connection)
                
                conn.close()
        finally:
            # Clean up
            shutil.rmtree(temp_dir)

    def test_database_schema_initialization(self, temp_db_path):
        """Test that database tables are properly initialized."""
        with patch('src.database.connection.DATABASE_PATH', temp_db_path):
            # Connect and create schema
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Read and execute schema SQL
            schema_path = Path(__file__).parent.parent / "src" / "database" / "schema.sql"
            with open(schema_path, 'r') as schema_file:
                schema_sql = schema_file.read()
            
            cursor.executescript(schema_sql)
            conn.commit()
            
            # Verify users table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'users'
            
            # Verify users table structure
            cursor.execute("PRAGMA table_info(users)")
            columns = [column[1] for column in cursor.fetchall()]
            expected_columns = ['id', 'login', 'password_hash', 'created_at', 'last_login']
            
            for column in expected_columns:
                assert column in columns
            
            # Verify primary key constraint
            cursor.execute("PRAGMA index_list(users)")
            indexes = cursor.fetchall()
            primary_key_exists = any(index[1] == 'sqlite_autoindex_users_1' for index in indexes)
            assert primary_key_exists
            
            cursor.close()
            conn.close()

    def test_database_multiple_connections(self, temp_db_path):
        """Test that multiple connections can be made to the same database."""
        with patch('src.database.connection.DATABASE_PATH', temp_db_path):
            # Create database with initial connection
            conn1 = get_db_connection()
            conn1.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER)")
            conn1.commit()
            conn1.close()
            
            # Make multiple connections
            connections = []
            for _ in range(5):
                conn = get_db_connection()
                connections.append(conn)
                
                # Verify table exists
                result = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='test_table'").fetchone()
                assert result is not None
                
                conn.close()
            
            assert len(connections) == 5

    def test_database_data_persistence(self, temp_db_path):
        """Test that data persists across connections."""
        with patch('src.database.connection.DATABASE_PATH', temp_db_path):
            # First connection - insert data
            conn1 = get_db_connection()
            conn1.execute("CREATE TABLE IF NOT EXISTS persistence_test (id INTEGER, data TEXT)")
            conn1.execute("INSERT INTO persistence_test (id, data) VALUES (1, 'test_data')")
            conn1.commit()
            conn1.close()
            
            # Second connection - verify data persists
            conn2 = get_db_connection()
            cursor = conn2.cursor()
            cursor.execute("SELECT data FROM persistence_test WHERE id = 1")
            result = cursor.fetchone()
            assert result is not None
            assert result[0] == 'test_data'
            cursor.close()
            conn2.close()

    def test_database_foreign_key_constraints(self, temp_db_path):
        """Test foreign key constraints behavior."""
        with patch('src.database.connection.DATABASE_PATH', temp_db_path):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create tables with foreign key constraint
            cursor.executescript('''
                CREATE TABLE IF NOT EXISTS parents (
                    id INTEGER PRIMARY KEY,
                    name TEXT
                );
                
                CREATE TABLE IF NOT EXISTS children (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    parent_id INTEGER,
                    FOREIGN KEY (parent_id) REFERENCES parents (id)
                );
            ''')
            conn.commit()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            conn.commit()
            
            # Test foreign key constraint
            try:
                # This should fail - inserting child with non-existent parent
                cursor.execute("INSERT INTO children (name, parent_id) VALUES ('child', 999)")
                conn.commit()
                pytest.fail("Foreign key constraint should have been violated")
            except sqlite3.IntegrityError:
                # Expected behavior
                conn.rollback()
            
            # Test valid insertion
            cursor.execute("INSERT INTO parents (name) VALUES ('parent')")
            parent_id = cursor.lastrowid
            cursor.execute("INSERT INTO children (name, parent_id) VALUES ('child', ?)", (parent_id,))
            conn.commit()
            
            # Verify insertion worked
            cursor.execute("SELECT * FROM children WHERE name = 'child'")
            result = cursor.fetchone()
            assert result is not None
            assert result[2] == parent_id
            
            cursor.close()
            conn.close()

    def test_database_unique_constraints(self, temp_db_path):
        """Test unique constraints on database tables."""
        with patch('src.database.connection.DATABASE_PATH', temp_db_path):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create table with unique constraint
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS unique_test (
                    id INTEGER PRIMARY KEY,
                    unique_field TEXT UNIQUE
                )
            ''')
            conn.commit()
            
            # Insert first record
            cursor.execute("INSERT INTO unique_test (unique_field) VALUES ('test')")
            conn.commit()
            
            # Try to insert duplicate - should fail
            try:
                cursor.execute("INSERT INTO unique_test (unique_field) VALUES ('test')")
                conn.commit()
                pytest.fail("Unique constraint should have been violated")
            except sqlite3.IntegrityError:
                # Expected behavior
                conn.rollback()
            
            # Insert different value - should work
            cursor.execute("INSERT INTO unique_test (unique_field) VALUES ('different')")
            conn.commit()
            
            cursor.close()
            conn.close()

    def test_database_auto_increment(self, temp_db_path):
        """Test auto-increment behavior for primary keys."""
        with patch('src.database.connection.DATABASE_PATH', temp_db_path):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create table with auto-increment primary key
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_inc_test (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT
                )
            ''')
            conn.commit()
            
            # Insert multiple records
            records = [('record1',), ('record2',), ('record3',)]
            cursor.executemany("INSERT INTO auto_inc_test (name) VALUES (?)", records)
            conn.commit()
            
            # Verify auto-increment worked
            cursor.execute("SELECT id, name FROM auto_inc_test ORDER BY id")
            results = cursor.fetchall()
            
            assert len(results) == 3
            assert results[0][0] == 1
            assert results[1][0] == 2
            assert results[2][0] == 3
            assert results[0][1] == 'record1'
            assert results[1][1] == 'record2'
            assert results[2][1] == 'record3'
            
            cursor.close()
            conn.close()

    def test_database_datetime_handling(self, temp_db_path):
        """Test datetime handling in database."""
        with patch('src.database.connection.DATABASE_PATH', temp_db_path):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create table with datetime column
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS datetime_test (
                    id INTEGER PRIMARY KEY,
                    event_name TEXT,
                    created_at DATETIME
                )
            ''')
            conn.commit()
            
            # Insert current datetime
            from datetime import datetime
            current_time = datetime.now()
            cursor.execute(
                "INSERT INTO datetime_test (event_name, created_at) VALUES (?, ?)",
                ('test_event', current_time)
            )
            conn.commit()
            
            # Verify datetime was stored correctly
            cursor.execute("SELECT created_at FROM datetime_test WHERE event_name = 'test_event'")
            result = cursor.fetchone()
            assert result is not None
            stored_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f')
            
            # Verify time is close to original (within 1 second)
            time_diff = abs((stored_time - current_time).total_seconds())
            assert time_diff < 1.0
            
            cursor.close()
            conn.close()

    def test_database_transaction_rollback(self):
        """Test transaction rollback on error."""
        # Create a temporary directory for the database
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, 'test.db')
        
        try:
            with patch('src.database.connection.DATABASE_PATH', temp_path):
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Create test table
                cursor.execute("CREATE TABLE IF NOT EXISTS rollback_test (id INTEGER, data TEXT)")
                conn.commit()
                
                # Start transaction
                conn.execute("BEGIN TRANSACTION")
                
                # Insert data
                cursor.execute("INSERT INTO rollback_test (id, data) VALUES (1, 'should_rollback')")
                
                # Verify data is in transaction but not committed yet
                cursor.execute("SELECT COUNT(*) FROM rollback_test")
                count_in_transaction = cursor.fetchone()[0]
                assert count_in_transaction == 1
                
                # Simulate error without committing
                # Rollback should happen automatically when connection is closed with exception
                
                try:
                    # Force an error
                    conn.execute("INVALID SQL")
                    pytest.fail("Should have raised an exception")
                except sqlite3.OperationalError:
                    # Expected - transaction should be rolled back
                    pass
                
                # Create a new connection to verify data was not committed
                conn2 = get_db_connection()
                cursor2 = conn2.cursor()
                cursor2.execute("SELECT COUNT(*) FROM rollback_test")
                count_after_rollback = cursor2.fetchone()[0]
                assert count_after_rollback == 0
                
                cursor2.close()
                conn2.close()
        finally:
            # Clean up
            shutil.rmtree(temp_dir)
            
            cursor.close()
            conn.close()

    def test_database_concurrent_access(self, temp_db_path):
        """Test concurrent database access."""
        import threading
        import time
        
        with patch('src.database.connection.DATABASE_PATH', temp_db_path):
            results = []
            errors = []
            
            def worker(worker_id):
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    
                    # Create table if not exists
                    cursor.execute("CREATE TABLE IF NOT EXISTS concurrent_test (id INTEGER, worker_id INTEGER)")
                    conn.commit()
                    
                    # Insert worker's data
                    cursor.execute("INSERT INTO concurrent_test (id, worker_id) VALUES (?, ?)", 
                                 (int(time.time() * 1000) % 10000, worker_id))
                    conn.commit()
                    
                    # Read data
                    cursor.execute("SELECT COUNT(*) FROM concurrent_test")
                    count = cursor.fetchone()[0]
                    results.append(count)
                    
                    cursor.close()
                    conn.close()
                    
                except Exception as e:
                    errors.append(str(e))
            
            # Create multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Wait for all threads to complete
            for thread in threads:
                thread.join()
            
            # Verify no errors occurred
            assert len(errors) == 0
            assert len(results) == 5
            
            # Verify all threads could access the database
            assert all(count > 0 for count in results)

    def test_database_memory_efficiency(self, temp_db_path):
        """Test database memory usage with large datasets."""
        with patch('src.database.connection.DATABASE_PATH', temp_db_path):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Create test table
            cursor.execute("CREATE TABLE IF NOT EXISTS memory_test (id INTEGER, data TEXT)")
            conn.commit()
            
            # Insert large dataset
            batch_size = 1000
            total_records = 5000
            
            for i in range(0, total_records, batch_size):
                records = [(j, f'data_{j}') for j in range(i, min(i + batch_size, total_records))]
                cursor.executemany("INSERT INTO memory_test (id, data) VALUES (?, ?)", records)
                
                # Commit in batches to avoid memory issues
                conn.commit()
            
            # Verify all records were inserted
            cursor.execute("SELECT COUNT(*) FROM memory_test")
            count = cursor.fetchone()[0]
            assert count == total_records
            
            cursor.close()
            conn.close()