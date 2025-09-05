import unittest

from src.database.connection import get_db_connection


class DatabaseTest(unittest.TestCase):
    def test_db_connection(self):
        conn = get_db_connection()
        self.assertIsNotNone(conn)
