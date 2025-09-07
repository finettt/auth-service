from src.crypto.utils import encrypt_password, verify_password


class TestCryptoUtils:
    """Test suite for crypto utility functions."""

    def test_encrypt_password_basic(self):
        """Test basic password encryption functionality."""
        password = "test_password_123"
        encrypted = encrypt_password(password)
        
        # Verify the encrypted result is a string
        assert isinstance(encrypted, str)
        
        # Verify the encrypted result is not empty
        assert len(encrypted) > 0
        
        # Verify bcrypt hash format (starts with $2b$ and has 60 characters)
        assert encrypted.startswith('$2b$')
        assert len(encrypted) == 60

    def test_encrypt_password_consistency(self):
        """Test that the same password always produces different encrypted results (due to salt)."""
        password = "consistent_password"
        encrypted1 = encrypt_password(password)
        encrypted2 = encrypt_password(password)
        
        # Different salts should produce different hashes
        assert encrypted1 != encrypted2
        
        # But both should be valid for the same password
        assert verify_password(password, encrypted1)
        assert verify_password(password, encrypted2)

    def test_encrypt_password_different_passwords(self):
        """Test that different passwords produce different encrypted results."""
        password1 = "password_one"
        password2 = "password_two"
        
        encrypted1 = encrypt_password(password1)
        encrypted2 = encrypt_password(password2)
        
        assert encrypted1 != encrypted2
        assert not verify_password(password1, encrypted2)
        assert not verify_password(password2, encrypted1)

    def test_encrypt_password_empty_string(self):
        """Test encryption with empty string password."""
        password = ""
        encrypted = encrypt_password(password)
        
        assert isinstance(encrypted, str)
        assert len(encrypted) == 60
        assert encrypted.startswith('$2b$')
        
        # Empty string should always produce different hashes due to salt
        encrypted2 = encrypt_password(password)
        assert encrypted != encrypted2
        assert verify_password(password, encrypted)
        assert verify_password(password, encrypted2)

    def test_encrypt_password_special_characters(self):
        """Test encryption with special characters."""
        password = "P@ssw0rd!@#$%^&*()"
        encrypted = encrypt_password(password)
        
        assert isinstance(encrypted, str)
        assert len(encrypted) == 60
        assert encrypted.startswith('$2b$')
        assert verify_password(password, encrypted)

    def test_encrypt_password_unicode(self):
        """Test encryption with unicode characters."""
        password = "пароль123"  # Russian characters
        encrypted = encrypt_password(password)
        
        assert isinstance(encrypted, str)
        assert len(encrypted) == 60
        assert encrypted.startswith('$2b$')
        assert verify_password(password, encrypted)

    def test_encrypt_password_long_password(self):
        """Test encryption with a very long password."""
        long_password = "a" * 1000  # 1000 character password
        encrypted = encrypt_password(long_password)
        
        assert isinstance(encrypted, str)
        assert len(encrypted) == 60
        assert encrypted.startswith('$2b$')
        assert verify_password(long_password, encrypted)

    def test_encrypt_password_numeric_only(self):
        """Test encryption with numeric-only password."""
        password = "1234567890"
        encrypted = encrypt_password(password)
        
        assert isinstance(encrypted, str)
        assert len(encrypted) == 60
        assert encrypted.startswith('$2b$')
        assert verify_password(password, encrypted)

    def test_encrypt_password_whitespace(self):
        """Test encryption with passwords containing whitespace."""
        password = "  password with spaces  "
        encrypted = encrypt_password(password)
        
        assert isinstance(encrypted, str)
        assert len(encrypted) == 60
        assert encrypted.startswith('$2b$')
        assert verify_password(password, encrypted)
        # Whitespace should be preserved and affect the hash
        assert not verify_password("passwordwithspaces", encrypted)

    def test_encrypt_password_newlines(self):
        """Test encryption with passwords containing newlines."""
        password = "password\nwith\nnewlines"
        encrypted = encrypt_password(password)
        
        assert isinstance(encrypted, str)
        assert len(encrypted) == 60
        assert encrypted.startswith('$2b$')
        assert verify_password(password, encrypted)

    def test_encrypt_password_tabs(self):
        """Test encryption with passwords containing tabs."""
        password = "password\twith\ttabs"
        encrypted = encrypt_password(password)
        
        assert isinstance(encrypted, str)
        assert len(encrypted) == 60
        assert encrypted.startswith('$2b$')
        assert verify_password(password, encrypted)

    def test_encrypt_password_case_sensitivity(self):
        """Test that encryption is case sensitive."""
        password_lower = "password"
        password_upper = "PASSWORD"
        
        encrypted_lower = encrypt_password(password_lower)
        encrypted_upper = encrypt_password(password_upper)
        
        assert encrypted_lower != encrypted_upper
        assert verify_password(password_lower, encrypted_lower)
        assert verify_password(password_upper, encrypted_upper)
        assert not verify_password(password_lower, encrypted_upper)
        assert not verify_password(password_upper, encrypted_lower)

    def test_encrypt_password_hex_format(self):
        """Test that encrypted password follows bcrypt format."""
        password = "test_hex_format"
        encrypted = encrypt_password(password)
        
        # Verify bcrypt format: $2b$cost$salt+hash
        assert isinstance(encrypted, str)
        assert encrypted.startswith('$2b$')
        
        # Split and verify parts (first element is empty due to leading $)
        parts = encrypted.split('$')
        assert len(parts) == 4
        assert parts[1] == '2b'  # algorithm identifier
        assert parts[2].isdigit()  # cost factor
        assert len(parts[3]) == 53  # salt + hash (22 + 31)

    def test_encrypt_password_performance(self):
        """Test that encryption is reasonably fast."""
        import time
        
        password = "performance_test_password"
        
        # Time the encryption
        start_time = time.time()
        encrypted = encrypt_password(password)
        end_time = time.time()
        
        # Should complete in less than 1 second for a single password
        assert (end_time - start_time) < 1.0
        
        # Verify we still get a valid result
        assert len(encrypted) == 60
        assert encrypted.startswith('$2b$')
        assert verify_password(password, encrypted)

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "test_password_123"
        encrypted = encrypt_password(password)
        
        assert verify_password(password, encrypted)

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password1 = "correct_password"
        password2 = "wrong_password"
        encrypted = encrypt_password(password1)
        
        assert not verify_password(password2, encrypted)

    def test_verify_password_timing_attack_resistant(self):
        """Test that verify_password is resistant to timing attacks."""
        import time
        import statistics
        
        password = "test_password"
        encrypted = encrypt_password(password)
        wrong_password = "test_passwor"  # One character different
        
        # Run multiple iterations to get stable timing measurements
        correct_times = []
        wrong_times = []
        
        iterations = 100
        
        for _ in range(iterations):
            # Test with correct password
            start_time = time.perf_counter()
            result1 = verify_password(password, encrypted)
            correct_times.append(time.perf_counter() - start_time)
            
            # Test with incorrect password of same length
            start_time = time.perf_counter()
            result2 = verify_password(wrong_password, encrypted)
            wrong_times.append(time.perf_counter() - start_time)
            
            # Verify results are as expected
            assert result1
            assert not result2
        
        # Calculate statistics
        correct_mean = statistics.mean(correct_times)
        wrong_mean = statistics.mean(wrong_times)
        correct_stdev = statistics.stdev(correct_times) if len(correct_times) > 1 else 0
        wrong_stdev = statistics.stdev(wrong_times) if len(wrong_times) > 1 else 0
        
        # Times should be very similar (constant-time comparison)
        # Use a reasonable tolerance based on standard deviation
        time_diff = abs(correct_mean - wrong_mean)
        max_acceptable_diff = max(correct_stdev, wrong_stdev) * 3  # 3 standard deviations
        
        # The difference should not be statistically significant
        assert time_diff < max_acceptable_diff or time_diff < 0.0001, \
            f"Timing difference too large: correct={correct_mean:.6f}s, wrong={wrong_mean:.6f}s, diff={time_diff:.6f}s"
        
        # Individual measurements should not vary too much (allow slightly higher tolerance)
        assert correct_stdev < 0.002, f"Correct password timing varies too much: stdev={correct_stdev:.6f}s"
        assert wrong_stdev < 0.002, f"Wrong password timing varies too much: stdev={wrong_stdev:.6f}s"