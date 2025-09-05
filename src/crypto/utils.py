from hashlib import sha3_384


def encrypt_password(password: str):
    generated = sha3_384(password.encode())
    return generated.hexdigest()
