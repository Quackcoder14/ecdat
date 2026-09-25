"""
Crypto Service for Python Service
Demonstrates real cryptographic operations that ECDAT can detect.
"""

import hashlib
import hmac
import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, ec, padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend


def generate_rsa_keypair(key_size: int = 2048):
    """
    Generate RSA key pair.
    ECDAT will detect: RSA key generation, key size
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    return private_key, public_key


def rsa_sign(private_key, message: bytes) -> bytes:
    """
    Sign message with RSA private key.
    ECDAT will detect: RSA signing, PKCS1v15 padding, SHA-256
    """
    signature = private_key.sign(
        message,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return signature


def rsa_verify(public_key, message: bytes, signature: bytes) -> bool:
    """
    Verify RSA signature.
    ECDAT will detect: RSA verification, PKCS1v15 padding, SHA-256
    """
    try:
        public_key.verify(
            signature,
            message,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def generate_ecdsa_keypair(curve_name: str = "secp256r1"):
    """
    Generate ECDSA key pair.
    ECDAT will detect: ECDSA key generation, curve
    """
    if curve_name == "secp256r1":
        curve = ec.SECP256R1()
    elif curve_name == "secp384r1":
        curve = ec.SECP384R1()
    elif curve_name == "secp521r1":
        curve = ec.SECP521R1()
    else:
        raise ValueError(f"Unsupported curve: {curve_name}")
    
    private_key = ec.generate_private_key(curve, default_backend())
    public_key = private_key.public_key()
    return private_key, public_key


def ecdsa_sign(private_key, message: bytes) -> bytes:
    """
    Sign message with ECDSA private key.
    ECDAT will detect: ECDSA signing, SHA-256
    """
    signature = private_key.sign(
        message,
        ec.ECDSA(hashes.SHA256())
    )
    return signature


def ecdsa_verify(public_key, message: bytes, signature: bytes) -> bool:
    """
    Verify ECDSA signature.
    ECDAT will detect: ECDSA verification
    """
    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return True
    except Exception:
        return False


def generate_ecdh_keypair(curve_name: str = "secp256r1"):
    """
    Generate ECDH key pair for key exchange.
    ECDAT will detect: ECDH key generation, curve
    """
    if curve_name == "secp256r1":
        curve = ec.SECP256R1()
    elif curve_name == "secp384r1":
        curve = ec.SECP384R1()
    elif curve_name == "secp521r1":
        curve = ec.SECP521R1()
    else:
        raise ValueError(f"Unsupported curve: {curve_name}")
    
    private_key = ec.generate_private_key(curve, default_backend())
    public_key = private_key.public_key()
    return private_key, public_key


def ecdh_key_exchange(private_key, peer_public_key) -> bytes:
    """
    Perform ECDH key exchange.
    ECDAT will detect: ECDH key agreement
    """
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    return shared_key


def aes_gcm_encrypt(key: bytes, plaintext: bytes, associated_data: bytes = None) -> tuple:
    """
    Encrypt data using AES-GCM.
    ECDAT will detect: AES encryption, GCM mode, key size
    """
    iv = os.urandom(12)
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    if associated_data:
        encryptor.authenticate_additional_data(associated_data)
    
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    return iv, ciphertext, encryptor.tag


def aes_gcm_decrypt(key: bytes, iv: bytes, ciphertext: bytes, tag: bytes, associated_data: bytes = None) -> bytes:
    """
    Decrypt data using AES-GCM.
    ECDAT will detect: AES decryption, GCM mode
    """
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    
    if associated_data:
        decryptor.authenticate_additional_data(associated_data)
    
    plaintext = decryptor.update(ciphertext) + decryptor.finalize()
    return plaintext


def derive_key_pbkdf2(password: bytes, salt: bytes, iterations: int = 100000, key_length: int = 32) -> bytes:
    """
    Derive key using PBKDF2.
    ECDAT will detect: PBKDF2, HMAC-SHA256
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_length,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password)


def sha256_hash(data: bytes) -> bytes:
    """
    Compute SHA-256 hash.
    ECDAT will detect: SHA-256 hashing
    """
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    digest.update(data)
    return digest.finalize()


def sha384_hash(data: bytes) -> bytes:
    """
    Compute SHA-384 hash.
    ECDAT will detect: SHA-384 hashing
    """
    digest = hashes.Hash(hashes.SHA384(), backend=default_backend())
    digest.update(data)
    return digest.finalize()


def hmac_sha256(key: bytes, message: bytes) -> bytes:
    """
    Compute HMAC-SHA256.
    ECDAT will detect: HMAC, SHA-256
    """
    h = hmac.new(key, message, hashlib.sha256)
    return h.digest()


def generate_jwt_rsa_key(key_size: int = 2048):
    """
    Generate RSA key for JWT signing.
    ECDAT will detect: RSA key generation for JWT
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
        backend=default_backend()
    )
    return private_key


def sign_jwt(private_key, payload: dict) -> str:
    """
    Sign JWT payload with RSA private key.
    ECDAT will detect: RSA signing for JWT
    """
    import jwt
    token = jwt.encode(payload, private_key, algorithm='RS256')
    return token


if __name__ == "__main__":
    # Demo usage - these will be scanned by ECDAT
    print("Generating RSA key pair...")
    rsa_private, rsa_public = generate_rsa_keypair(2048)
    
    message = b"Hello, ECDAT!"
    signature = rsa_sign(rsa_private, message)
    verified = rsa_verify(rsa_public, message, signature)
    print(f"RSA sign/verify: {verified}")
    
    print("Generating ECDSA key pair...")
    ecdsa_private, ecdsa_public = generate_ecdsa_keypair("secp256r1")
    sig = ecdsa_sign(ecdsa_private, message)
    verified = ecdsa_verify(ecdsa_public, message, sig)
    print(f"ECDSA sign/verify: {verified}")
    
    print("Generating ECDH key pair...")
    ecdh_private, ecdh_public = generate_ecdh_keypair("secp256r1")
    shared = ecdh_key_exchange(ecdh_private, ecdh_public)
    print(f"ECDH shared key length: {len(shared)}")
    
    print("AES-GCM encryption...")
    key = os.urandom(32)
    iv, ct, tag = aes_gcm_encrypt(key, b"Secret data", b"auth-data")
    decrypted = aes_gcm_decrypt(key, iv, ct, tag, b"auth-data")
    print(f"AES-GCM round-trip: {decrypted == b'Secret data'}")
    
    print("PBKDF2 key derivation...")
    salt = os.urandom(16)
    key = derive_key_pbkdf2(b"password123", salt)
    print(f"Derived key length: {len(key)}")
    
    print("SHA-256 hashing...")
    digest = sha256_hash(b"test data")
    print(f"SHA-256: {digest.hex()}")
    
    print("HMAC-SHA256...")
    hmac_tag = hmac_sha256(b"secret-key", b"message")
    print(f"HMAC: {hmac_tag.hex()}")
    
    print("JWT signing...")
    jwt_key = generate_jwt_rsa_key(2048)
    token = sign_jwt(jwt_key, {"sub": "user123", "exp": 9999999999})
    print(f"JWT token generated")