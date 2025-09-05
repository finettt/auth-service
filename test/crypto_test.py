import unittest

from src.crypto.utils import encrypt_password


class CryptoUtilsTest(unittest.TestCase):
    def test_hash(self):
        hashed_string = "3f7bfd572e7ceca53c9bcbc5362ee28bd7909487bf51bbddf1233c2acc3ba1c040cc2b68328ff8afd1538d2fc963dd73"
        test_string = "test_string"
        self.assertEqual(hashed_string,encrypt_password(test_string))