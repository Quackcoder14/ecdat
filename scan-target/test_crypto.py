"""
Test file with cryptographic patterns for scanning
"""

import hashlib
import hmac
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def test_sha256():
    """Test SHA-256 hashing"""
    data = b"test data"
    digest = hashlib.sha256(data).hexdigest()
    return digest


def test_hmac():
    """Test HMAC"""
    key = b"secret_key"
    message = b"test message"
    signature = hmac.new(key, message, hashlib.sha256).hexdigest()
    return signature


def test_rsa():
    """Test RSA key generation"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    return private_key


def test_aes():
    """Test AES encryption"""
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    key = b"32_byte_key_for_aes_encryption_123"
    iv = b"16_byte_iv_1234"
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    return cipher


def test_pbkdf2():
    """Test PBKDF2 key derivation"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"salt",
        iterations=100000
    )
    return kdf


if __name__ == "__main__":
    print("Testing cryptographic patterns...")
    print(f"SHA-256: {test_sha256()}")
    print(f"HMAC: {test_hmac()}")
    print(f"RSA key generated: {test_rsa()}")
    print(f"AES cipher created: {test_aes()}")
    print(f"PBKDF2 KDF created: {test_pbkdf2()}")
