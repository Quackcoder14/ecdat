package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/des"
	"crypto/ecdsa"
	"crypto/elliptic"
	"crypto/hmac"
	"crypto/md5"
	"crypto/rand"
	"crypto/rsa"
	"crypto/sha1"
	"crypto/sha256"
	"crypto/sha512"
	"crypto/tls"
	"crypto/x509"
	"encoding/hex"
	"encoding/pem"
	"fmt"
	"golang.org/x/crypto/chacha20poly1305"
	"golang.org/x/crypto/pbkdf2"
	"hash"
)

// CryptoService demonstrates real cryptographic operations in Go that ECDAT can detect.
type CryptoService struct{}

// GenerateRSAKeyPair generates an RSA key pair.
// ECDAT will detect: RSA key generation, key size
func (cs *CryptoService) GenerateRSAKeyPair(keySize int) (*rsa.PrivateKey, *rsa.PublicKey) {
	privateKey, err := rsa.GenerateKey(rand.Reader, keySize)
	if err != nil {
		panic(err)
	}
	return privateKey, &privateKey.PublicKey
}

// RSASign signs data with RSA private key.
// ECDAT will detect: RSA signing, PKCS1v15, SHA-256
func (cs *CryptoService) RSASign(privateKey *rsa.PrivateKey, data []byte) ([]byte, error) {
	hash := sha256.Sum256(data)
	signature, err := rsa.SignPKCS1v15(rand.Reader, privateKey, crypto.SHA256, hash[:])
	if err != nil {
		return nil, err
	}
	return signature, nil
}

// RSAVerify verifies an RSA signature.
// ECDAT will detect: RSA verification, PKCS1v15, SHA-256
func (cs *CryptoService) RSAVerify(publicKey *rsa.PublicKey, data, signature []byte) error {
	hash := sha256.Sum256(data)
	return rsa.VerifyPKCS1v15(&publicKey, crypto.SHA256, hash[:], signature)
}

// GenerateECDSAKeyPair generates an ECDSA key pair.
// ECDAT will detect: ECDSA key generation, curve
func (cs *CryptoService) GenerateECDSAKeyPair(curve elliptic.Curve) (*ecdsa.PrivateKey, *ecdsa.PublicKey) {
	privateKey, err := ecdsa.GenerateKey(curve, rand.Reader)
	if err != nil {
		panic(err)
	}
	return privateKey, &privateKey.PublicKey
}

// ECDSASign signs data with ECDSA private key.
// ECDAT will detect: ECDSA signing, SHA-256
func (cs *CryptoService) ECDSASign(privateKey *ecdsa.PrivateKey, data []byte) ([]byte, error) {
	hash := sha256.Sum256(data)
	r, s, err := ecdsa.Sign(rand.Reader, privateKey, hash[:])
	if err != nil {
		return nil, err
	}
	// Serialize as ASN.1 DER
	return marshalECDSASignature(r, s)
}

// ECDSAVerify verifies an ECDSA signature.
// ECDAT will detect: ECDSA verification, SHA-256
func (cs *CryptoService) ECDSAVerify(publicKey *ecdsa.PublicKey, data, signature []byte) bool {
	hash := sha256.Sum256(data)
	r, s := unmarshalECDSASignature(signature)
	return ecdsa.Verify(&publicKey, hash[:], r, s)
}

// GenerateECDHKeyPair generates an ECDH key pair.
// ECDAT will detect: ECDH key generation, curve
func (cs *CryptoService) GenerateECDHKeyPair(curve elliptic.Curve) (*ecdsa.PrivateKey, *ecdsa.PublicKey) {
	privateKey, err := ecdsa.GenerateKey(curve, rand.Reader)
	if err != nil {
		panic(err)
	}
	return privateKey, &privateKey.PublicKey
}

// ECDHKeyAgreement performs ECDH key agreement.
// ECDAT will detect: ECDH key agreement, key derivation
func (cs *CryptoService) ECDHKeyAgreement(privateKey *ecdsa.PrivateKey, publicKey *ecdsa.PublicKey) []byte {
	sharedX, _ := publicKey.Curve.ScalarMult(publicKey.X, publicKey.Y, privateKey.D.Bytes())
	return sharedX.Bytes()
}

// AESGCMEncrypt encrypts data using AES-GCM.
// ECDAT will detect: AES encryption, GCM mode, key size
func (cs *CryptoService) AESGCMEncrypt(key, plaintext, aad []byte) ([]byte, []byte, []byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, nil, nil, err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, nil, nil, err
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err := rand.Read(nonce); err != nil {
		return nil, nil, nil, err
	}

	ciphertext := gcm.Seal(nil, nonce, plaintext, nil)
	return nonce, ciphertext, nil, nil
}

// AESGCMDecrypt decrypts data using AES-GCM.
// ECDAT will detect: AES decryption, GCM mode
func (cs *CryptoService) AESGCMDecrypt(key, nonce, ciphertext, aad []byte) ([]byte, error) {
	block, err := aes.NewCipher(key)
	if err != nil {
		return nil, err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, err
	}

	plaintext, err := gcm.Open(nil, nonce, ciphertext, aad)
	if err != nil {
		return nil, err
	}
	return plaintext, nil
}

// GenerateAESKey generates an AES key.
// ECDAT will detect: AES key generation
func (cs *CryptoService) GenerateAESKey(keySize int) ([]byte, error) {
	key := make([]byte, keySize/8)
	if _, err := rand.Read(key); err != nil {
		return nil, err
	}
	return key, nil
}

// PBKDF2KeyDerivation derives a key using PBKDF2.
// ECDAT will detect: PBKDF2, HMAC-SHA256
func (cs *CryptoService) PBKDF2KeyDerivation(password, salt []byte, iterations, keyLength int) []byte {
	return pbkdf2.Key([]byte(password), salt, iterations, len(password), sha256.New)
}

// SHA256 hashing.
// ECDAT will detect: SHA-256 hashing
func (cs *CryptoService) SHA256(data []byte) []byte {
	hash := sha256.Sum256(data)
	return hash[:]
}

// SHA512 hashing.
// ECDAT will detect: SHA-512 hashing
func (cs *CryptoService) SHA512(data []byte) []byte {
	hash := sha512.Sum512(data)
	return hash[:]
}

// HMACSHA256 computes HMAC-SHA256.
// ECDAT will detect: HMAC, SHA-256
func (cs *CryptoService) HMACSHA256(key, data []byte) []byte {
	h := hmac.New(sha256.New, key)
	h.Write(data)
	return h.Sum(nil)
}

// GenerateRSAKeyPair generates an RSA key pair for JWT.
// ECDAT will detect: RSA key generation for JWT
func (cs *CryptoService) GenerateJWTKeyPair(keySize int) (*rsa.PrivateKey, *rsa.PublicKey) {
	privateKey, err := rsa.GenerateKey(rand.Reader, keySize)
	if err != nil {
		panic(err)
	}
	return privateKey, &privateKey.PublicKey
}

// LoadCertificate loads a certificate from PEM file.
// ECDAT will detect: Certificate loading, X.509 parsing
func (cs *CryptoService) LoadCertificate(filePath string) (*x509.Certificate, error) {
	pemData, err := os.ReadFile(filePath)
	if err != nil {
		return nil, err
	}
	block, _ := pem.Decode(pemData)
	if block == nil {
		return nil, fmt.Errorf("failed to decode PEM")
	}
	cert, err := x509.ParseCertificate(block.Bytes)
	if err != nil {
		return nil, err
	}
	return cert, nil
}

// CreateTLSConfig creates a TLS configuration.
// ECDAT will detect: TLS configuration, cipher suites
func (cs *CryptoService) CreateTLSConfig() *tls.Config {
	return &tls.Config{
		MinVersion: tls.VersionTLS12,
		CipherSuites: []uint16{
			tls.TLS_AES_256_GCM_SHA384,
			tls.TLS_CHACHA20_POLY1305_SHA256,
			tls.TLS_AES_128_GCM_SHA256,
			tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
			tls.TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256,
		},
		MinVersion: tls.VersionTLS12,
	}
}

// GenerateJWTKeyPair generates an RSA key pair for JWT.
// ECDAT will detect: RSA key generation for JWT
func (cs *CryptoService) GenerateJWTKeyPair(keySize int) (*rsa.PrivateKey, *rsa.PublicKey) {
	privateKey, err := rsa.GenerateKey(rand.Reader, keySize)
	if err != nil {
		panic(err)
	}
	return privateKey, &privateKey.PublicKey
}

// DES3Encrypt encrypts data using 3DES (legacy/deprecated).
// ECDAT will detect: 3DES encryption (legacy/deprecated)
func (cs *CryptoService) DES3Encrypt(key, data []byte) ([]byte, error) {
	block, err := des.NewTripleDESCipher(key)
	if err != nil {
		return nil, err
	}
	iv := make([]byte, des.BlockSize)
	if _, err := rand.Read(iv); err != nil {
		return nil, err
	}
	ciphertext := make([]byte, len(data))
	mode := cipher.NewCBCEncrypter(block, iv)
	mode.CryptBlocks(ciphertext, data)
	return ciphertext, nil
}

// MD5 hashing (weak).
// ECDAT will detect: MD5 hashing (weak)
func (cs *CryptoService) MD5(data []byte) []byte {
	hash := md5.Sum(data)
	return hash[:]
}

// SHA1 hashing (weak).
// ECDAT will detect: SHA-1 hashing (weak)
func (cs *CryptoService) SHA1(data []byte) []byte {
	hash := sha1.Sum(data)
	return hash[:]
}

// ChaCha20-Poly1305 encryption.
// ECDAT will detect: ChaCha20-Poly1305 encryption
func (cs *CryptoService) ChaCha20Poly1305Encrypt(key, plaintext, aad []byte) ([]byte, []byte, error) {
	aead, err := chacha20poly1305.New(key)
	if err != nil {
		return nil, nil, err
	}
	nonce := make([]byte, aead.NonceSize())
	if _, err := rand.Read(nonce); err != nil {
		return nil, nil, err
	}
	ciphertext := aead.Seal(nil, nonce, plaintext, aad)
	return nonce, ciphertext, nil
}

// Helper functions
func marshalECDSASignature(r, s *big.Int) ([]byte, error) {
	return asn1.Marshal(struct {
		R, S *big.Int
	}{r, s})
}

func unmarshalECDSASignature(sig []byte) (*big.Int, *big.Int) {
	var sig struct {
		R, S *big.Int
	}
	asn1.Unmarshal(sig, &sig)
	return sig.R, sig.S
}

func main() {
	cs := &CryptoService{}
	fmt.Println("Go Crypto Service Demo - ECDAT will detect these operations\n")

	// RSA
	fmt.Println("Generating RSA-2048 key pair...")
	rsaPrivate, rsaPublic := cs.GenerateRSAKeyPair(2048)
	message := []byte("Hello, ECDAT!")
	rsaSig, _ := cs.RSASign(rsaPrivate, []byte("Hello, ECDAT!"))
	rsaErr := cs.RSAVerify(rsaPublic, []byte("Hello, ECDAT!"), rsaSig)
	fmt.Printf("RSA-2048 sign/verify: %v\n", rsaErr == nil)

	// ECDSA
	fmt.Println("\nGenerating ECDSA P-256 key pair...")
	ecdsaPrivate, ecdsaPublic := cs.GenerateECDSAKeyPair(elliptic.P256())
	ecdsaSig, _ := cs.ECDSASign(ecdsaPrivate, []byte("Hello, ECDAT!"))
	ecdsaVerified := cs.ECDSAVerify(ecdsaPublic, []byte("Hello, ECDAT!"), ecdsaSig)
	fmt.Printf("ECDSA P-256 sign/verify: %v\n", ecdsaVerified)

	// ECDH
	fmt.Println("\nGenerating ECDH P-256 key pair...")
	ecdhPrivate1, ecdhPublic1 := cs.GenerateECDHKeyPair(elliptic.P256())
	_, ecdhPublic2 := cs.GenerateECDHKeyPair(elliptic.P256())
	shared1 := cs.ECDHKeyAgreement(ecdhPrivate1, ecdhPublic2)
	shared2 := cs.ECDHKeyAgreement(ecdhPrivate1, ecdhPublic2) // Using same for demo
	fmt.Printf("ECDH shared secret length: %d\n", len(shared1))

	// AES-GCM
	fmt.Println("\nAES-256-GCM encryption...")
	aesKey, _ := cs.GenerateAESKey(256)
	plaintext := []byte("Secret data")
	aad := []byte("auth-data")
	nonce, ciphertext, _, _ := cs.AESGCMEncrypt(aesKey, plaintext, aad)
	decrypted, _ := cs.AESGCMDecrypt(key, nonce, ciphertext, aad)
	fmt.Printf("AES-256-GCM round-trip: %v\n", string(decrypted) == "Secret data")

	// PBKDF2
	fmt.Println("\nPBKDF2 key derivation...")
	salt := make([]byte, 16)
	rand.Read(salt)
	pbkdf2Key := pbkdf2.Key([]byte("password123"), salt, 100000, 32, sha256.New)
	fmt.Printf("PBKDF2 derived key length: %d\n", len(pbkdf2Key))

	// SHA-256
	fmt.Println("\nSHA-256 hashing...")
	hash256 := sha256.Sum256([]byte("test data"))
	fmt.Printf("SHA-256: %x\n", hash256)

	// SHA-512
	hash512 := sha512.Sum512([]byte("test data"))
	fmt.Printf("SHA-512: %x\n", hash512)

	// HMAC-SHA256
	fmt.Println("\nHMAC-SHA256...")
	hmacKey := make([]byte, 32)
	rand.Read(hmacKey)
	hmacTag := hmac.New(sha256.New, hmacKey)
	hmacTag.Write([]byte("message"))
	fmt.Printf("HMAC-SHA256: %x\n", hmacTag.Sum(nil))

	// 3DES (legacy)
	fmt.Println("\n3DES encryption (LEGACY/DEPRECATED)...")
	des3Key := make([]byte, 24)
	rand.Read(des3Key)
	block, _ := des.NewTripleDESCipher(des3Key)
	iv := make([]byte, des.BlockSize)
	rand.Read(iv)
	mode := cipher.NewCBCEncrypter(block, iv)
	ciphertext := make([]byte, len([]byte("legacy data")))
	mode.CryptBlocks(ciphertext, []byte("legacy data"))
	fmt.Printf("3DES ciphertext length: %d\n", len(ciphertext))

	// MD5 (weak)
	fmt.Println("\nMD5 hashing (WEAK)...")
	md5Hash := md5.Sum([]byte("test data"))
	fmt.Printf("MD5: %x\n", md5Hash)

	// SHA-1 (weak)
	fmt.Println("\nSHA-1 hashing (WEAK)...")
	sha1Hash := sha1.Sum([]byte("test data"))
	fmt.Printf("SHA-1: %x\n", sha1Hash)

	// ChaCha20-Poly1305
	fmt.Println("\nChaCha20-Poly1305 encryption...")
	chachaKey := make([]byte, chacha20poly1305.KeySize)
	rand.Read(chachaKey)
	aead, _ := chacha20poly1305.New(chachaKey)
	nonce := make([]byte, aead.NonceSize())
	rand.Read(nonce)
	chachaCiphertext := aead.Seal(nil, nonce, []byte("chacha data"), []byte("aad"))
	fmt.Printf("ChaCha20-Poly1305 ciphertext length: %d\n", len(chachaCiphertext))

	fmt.Println("\nAll crypto operations completed - ECDAT should detect these operations!")
}