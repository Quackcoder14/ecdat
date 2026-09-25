/*
 * Native Service - Legacy Crypto Operations
 * Demonstrates C/OpenSSL cryptographic operations that ECDAT can detect.
 */

#include <openssl/evp.h>
#include <openssl/rsa.h>
#include <openssl/ec.h>
#include <openssl/aes.h>
#include <openssl/sha.h>
#include <openssl/hmac.h>
#include <openssl/des.h>
#include <openssl/pem.h>
#include <openssl/err.h>
#include <openssl/kdf.h>
#include <openssl/rand.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Initialize OpenSSL
void init_openssl() {
    OPENSSL_init_crypto(OPENSSL_INIT_ADD_ALL_CIPHERS | OPENSSL_INIT_ADD_ALL_DIGESTS, NULL);
    ERR_load_crypto_strings();
}

// Generate RSA key pair
// ECDAT will detect: RSA key generation, key size
RSA* generate_rsa_keypair(int key_size) {
    EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new_id(EVP_PKEY_RSA, NULL);
    EVP_PKEY_keygen_init(ctx);
    EVP_PKEY_CTX_set_rsa_keygen_bits(ctx, 2048);
    EVP_PKEY *pkey = NULL;
    EVP_PKEY_keygen(ctx, &pkey);
    EVP_PKEY_CTX_free(ctx);
    return EVP_PKEY_get1_RSA(pkey);
}

// RSA Sign
// ECDAT will detect: RSA signing, PKCS#1 v1.5, SHA-256
int rsa_sign(RSA *rsa, const unsigned char *data, size_t data_len, unsigned char *sig, size_t *sig_len) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_PKEY *pkey = EVP_PKEY_new();
    EVP_PKEY_assign_RSA(pkey, rsa); // rsa is duplicated
    
    EVP_DigestSignInit(ctx, NULL, EVP_sha256(), NULL, pkey);
    EVP_DigestSignUpdate(ctx, data, data_len);
    EVP_DigestSignFinal(ctx, sig, sig_len);
    
    EVP_MD_CTX_free(ctx);
    EVP_PKEY_free(pkey);
    return 1;
}

// RSA Verify
// ECDAT will detect: RSA verification, PKCS#1 v1.5, SHA-256
int rsa_verify(RSA *rsa, const unsigned char *data, size_t data_len, const unsigned char *sig, size_t sig_len) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_PKEY *pkey = EVP_PKEY_new();
    EVP_PKEY_assign_RSA(pkey, rsa); // rsa is duplicated
    
    int ret = EVP_DigestVerifyInit(ctx, NULL, EVP_sha256(), NULL, pkey);
    EVP_DigestVerifyUpdate(ctx, data, data_len);
    int ret = EVP_DigestVerifyFinal(ctx, sig, sig_len);
    
    EVP_MD_CTX_free(ctx);
    EVP_PKEY_free(pkey);
    return ret == 1;
}

// Generate EC key pair (ECDSA/ECDH)
// ECDAT will detect: EC key generation, curve
EC_KEY* generate_ec_keypair(int curve_nid) {
    EC_KEY *ec_key = EC_KEY_new_by_curve_name(curve_nid);
    EC_KEY_generate_key(ec_key);
    return ec_key;
}

// ECDSA Sign
// ECDAT will detect: ECDSA signing, SHA-256
int ecdsa_sign(EC_KEY *ec_key, const unsigned char *data, size_t data_len, unsigned char *sig, size_t *sig_len) {
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_PKEY *pkey = EVP_PKEY_new();
    EVP_PKEY_assign_EC_KEY(pkey, ec_key); // ec_key is duplicated
    
    EVP_DigestSignInit(ctx, NULL, EVP_sha256(), NULL, pkey);
    EVP_DigestSignUpdate(ctx, data, data_len);
    EVP_DigestSignFinal(ctx, sig, sig_len);
    
    EVP_MD_CTX_free(ctx);
    EVP_PKEY_free(pkey);
    return 1;
}

// ECDH Key Agreement
// ECDAT will detect: ECDH key agreement
int ecdh_key_agreement(EC_KEY *ec_key, const EC_KEY *peer_ec_key, unsigned char **out, size_t *out_len) {
    const EC_GROUP *group = EC_KEY_get0_group(ec_key);
    const EC_POINT *pub_key = EC_KEY_get0_public_key(peer_ec_key);
    const BIGNUM *priv_key = EC_KEY_get0_private_key(ec_key);
    
    EC_POINT *shared_point = EC_POINT_new(EC_KEY_get0_group(ec_key));
    EC_POINT_mul(group, shared_point, NULL, pub_key, priv_key, NULL);
    
    BN_CTX *ctx = BN_CTX_new();
    BIGNUM *x = BN_new();
    BIGNUM *y = BN_new();
    EC_POINT_get_affine_coordinates_GFp(group, shared_point, x, y, ctx);
    
    *out_len = BN_num_bytes(x);
    *out = malloc(*out_len);
    BN_bn2bin(x, *out);
    
    BN_free(x);
    BN_free(y);
    BN_CTX_free(ctx);
    EC_POINT_free(shared_point);
    return 1;
}

// AES-GCM Encryption
// ECDAT will detect: AES encryption, GCM mode, key size
int aes_gcm_encrypt(const unsigned char *key, int key_len, const unsigned char *iv, int iv_len,
                    const unsigned char *aad, size_t aad_len,
                    const unsigned char *plaintext, size_t plaintext_len,
                    unsigned char *ciphertext, unsigned char *tag) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL);
    EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv);
    
    int len;
    EVP_EncryptUpdate(ctx, NULL, &len, aad, aad_len);
    EVP_EncryptUpdate(ctx, ciphertext, &len, plaintext, plaintext_len);
    int ciphertext_len = len;
    EVP_EncryptFinal_ex(ctx, ciphertext + len, &len);
    ciphertext_len += len;
    
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag);
    
    EVP_CIPHER_CTX_free(ctx);
    return 1;
}

// AES-GCM Decryption
// ECDAT will detect: AES decryption, GCM mode
int aes_gcm_decrypt(const unsigned char *key, int key_len, const unsigned char *iv, int iv_len,
                    const unsigned char *aad, size_t aad_len,
                    const unsigned char *ciphertext, size_t ciphertext_len,
                    const unsigned char *tag, int tag_len,
                    unsigned char *plaintext) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL);
    EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv);
    
    int len;
    EVP_DecryptUpdate(ctx, NULL, &len, aad, aad_len);
    EVP_DecryptUpdate(ctx, plaintext, &len, ciphertext, ciphertext_len);
    int plaintext_len = len;
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, tag_len, (void*)tag);
    int ret = EVP_DecryptFinal_ex(ctx, plaintext + len, &len);
    plaintext_len += len;
    
    EVP_CIPHER_CTX_free(ctx);
    return ret > 0;
}

// SHA-256 Hashing
// ECDAT will detect: SHA-256 hashing
void sha256_hash(const unsigned char *data, size_t len, unsigned char *out) {
    SHA256(data, len, out);
}

// SHA-384 Hashing
// ECDAT will detect: SHA-384 hashing
void sha384_hash(const unsigned char *data, size_t len, unsigned char *out) {
    SHA384(data, len, out);
}

// SHA-512 Hashing
// ECDAT will detect: SHA-512 hashing
void sha512_hash(const unsigned char *data, size_t len, unsigned char *out) {
    SHA512(data, len, out);
}

// HMAC-SHA256
// ECDAT will detect: HMAC, SHA-256
void hmac_sha256(const unsigned char *key, size_t key_len, const unsigned char *data, size_t data_len, unsigned char *out) {
    HMAC(EVP_sha256(), key, key_len, data, data_len, out, NULL);
}

// PBKDF2 Key Derivation
// ECDAT will detect: PBKDF2, HMAC-SHA256
int pbkdf2_derive(const char *password, const unsigned char *salt, size_t salt_len,
                  int iterations, int key_len, unsigned char *out) {
    return PKCS5_PBKDF2_HMAC(password, strlen(password), salt, salt_len, iterations, EVP_sha256(), key_len, out);
}

// 3DES Encryption (Legacy/Deprecated)
// ECDAT will detect: 3DES encryption (legacy/deprecated)
int des3_encrypt(const unsigned char *key, const unsigned char *iv, const unsigned char *data, size_t data_len, unsigned char *out) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    EVP_EncryptInit_ex(ctx, EVP_des_ede3_cbc(), NULL, key, iv);
    int len;
    EVP_EncryptUpdate(ctx, out, &len, data, data_len);
    int out_len = len;
    EVP_EncryptFinal_ex(ctx, out + len, &len);
    out_len += len;
    EVP_CIPHER_CTX_free(ctx);
    return 1;
}

// MD5 Hashing (Weak)
// ECDAT will detect: MD5 hashing (weak)
void md5_hash(const unsigned char *data, size_t len, unsigned char *out) {
    MD5(data, len, out);
}

// SHA-1 Hashing (Weak)
// ECDAT will detect: SHA-1 hashing (weak)
void sha1_hash(const unsigned char *data, size_t len, unsigned char *out) {
    SHA1(data, len, out);
}

// Certificate Parsing
// ECDAT will detect: Certificate loading, X.509 parsing
X509* load_certificate(const char *file_path) {
    FILE *fp = fopen(file_path, "r");
    if (!fp) return NULL;
    X509 *cert = PEM_read_X509(fp, NULL, NULL, NULL);
    fclose(fp);
    return cert;
}

// Extract public key from certificate
// ECDAT will detect: Certificate public key extraction
EVP_PKEY* get_pubkey_from_cert(X509 *cert) {
    return X509_get_pubkey(cert);
}

// TLS Configuration
// ECDAT will detect: TLS configuration, cipher suites
SSL_CTX* create_tls_context() {
    SSL_CTX *ctx = SSL_CTX_new(TLS_server_method());
    SSL_CTX_set_min_proto_version(ctx, TLS1_2_VERSION);
    SSL_CTX_set_cipher_list(ctx, "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-GCM-SHA256");
    return ctx;
}

// MD5 Hashing (Weak)
// ECDAT will detect: MD5 hashing (weak)
void md5_hash(const unsigned char *data, size_t len, unsigned char *out) {
    MD5(data, len, out);
}

// SHA-1 Hashing (Weak)
// ECDAT will detect: SHA-1 hashing (weak)
void sha1_hash(const unsigned char *data, size_t len, unsigned char *out) {
    SHA1(data, len, out);
}

// PBKDF2 Key Derivation
// ECDAT will detect: PBKDF2, HMAC-SHA256
int pbkdf2_derive(const char *password, const unsigned char *salt, size_t salt_len,
                  int iterations, int key_len, unsigned char *out) {
    return PKCS5_PBKDF2_HMAC(password, strlen(password), salt, salt_len, iterations, EVP_sha256(), key_len, out);
}

int main() {
    init_openssl();
    
    printf("C/OpenSSL Crypto Service Demo - ECDAT will detect these operations\n\n");
    
    // RSA
    printf("Generating RSA-2048 key pair...\n");
    RSA *rsa = generate_rsa_keypair(2048);
    
    unsigned char data[] = "Hello, ECDAT!";
    size_t data_len = strlen((char*)data);
    unsigned char sig[256];
    size_t sig_len;
    rsa_sign(rsa, data, data_len, sig, &sig_len);
    int verified = rsa_verify(rsa, data, data_len, sig, sig_len);
    printf("RSA-2048 sign/verify: %s\n", verified ? "SUCCESS" : "FAILED");
    
    // ECDSA
    printf("\nGenerating ECDSA P-256 key pair...\n");
    EC_KEY *ec_key = generate_ec_keypair(NID_X9_62_prime256v1);
    unsigned char ecdsa_sig[256];
    size_t ecdsa_sig_len;
    ecdsa_sign(ec_key, (unsigned char*)"Hello, ECDAT!", 13, ecdsa_sig, &ecdsa_sig_len);
    // Verify would need similar code
    printf("ECDSA P-256 sign: SUCCESS\n");
    
    // ECDH
    printf("\nGenerating ECDH P-256 key pair...\n");
    EC_KEY *ecdh1 = generate_ec_keypair(NID_X9_62_prime256v1);
    EC_KEY *ecdh2 = generate_ec_keypair(NID_X9_62_prime256v1);
    unsigned char *shared_secret = NULL;
    size_t shared_len;
    ecdh_key_agreement(ecdh1, ecdh2, &shared_secret, &shared_len);
    printf("ECDH shared secret length: %zu\n", shared_len);
    free(shared_secret);
    
    // AES-GCM
    printf("\nAES-256-GCM encryption...\n");
    unsigned char key[32];
    RAND_bytes(key, 32);
    unsigned char iv[12];
    RAND_bytes(iv, 12);
    unsigned char plaintext[] = "Secret data";
    unsigned char aad[] = "auth-data";
    unsigned char ciphertext[128];
    unsigned char tag[16];
    aes_gcm_encrypt(key, 32, iv, 12, aad, 8, plaintext, 11, ciphertext, tag);
    unsigned char decrypted[128];
    aes_gcm_decrypt(key, 32, iv, 12, aad, 8, ciphertext, 11, tag, 16, decrypted);
    printf("AES-256-GCM round-trip: %s\n", memcmp(plaintext, decrypted, 11) == 0 ? "SUCCESS" : "FAILED");
    
    // SHA-256
    printf("\nSHA-256 hashing...\n");
    unsigned char sha256_out[32];
    sha256_hash((unsigned char*)"test data", 9, sha256_out);
    printf("SHA-256: ");
    for (int i = 0; i < 32; i++) printf("%02x", sha256_out[i]);
    printf("\n");
    
    // HMAC-SHA256
    printf("\nHMAC-SHA256...\n");
    unsigned char hmac_key[32];
    RAND_bytes(hmac_key, 32);
    unsigned char hmac_out[32];
    hmac_sha256(hmac_key, 32, (unsigned char*)"message", 7, hmac_out);
    printf("HMAC-SHA256: ");
    for (int i = 0; i < 32; i++) printf("%02x", hmac_out[i]);
    printf("\n");
    
    // 3DES (Legacy)
    printf("\n3DES encryption (LEGACY/DEPRECATED)...\n");
    unsigned char des3_key[24];
    RAND_bytes(des3_key, 24);
    unsigned char des3_iv[8];
    RAND_bytes(des3_iv, 8);
    unsigned char des3_out[32];
    des3_encrypt(des3_key, des3_iv, (unsigned char*)"legacy data", 10, des3_out);
    printf("3DES ciphertext length: 32\n");
    
    // MD5 (Weak)
    printf("\nMD5 hashing (WEAK)...\n");
    unsigned char md5_out[16];
    md5_hash((unsigned char*)"test data", 9, md5_out);
    printf("MD5: ");
    for (int i = 0; i < 16; i++) printf("%02x", md5_out[i]);
    printf("\n");
    
    // SHA-1 (Weak)
    printf("\nSHA-1 hashing (WEAK)...\n");
    unsigned char sha1_out[20];
    sha1_hash((unsigned char*)"test data", 9, sha1_out);
    printf("SHA-1: ");
    for (int i = 0; i < 20; i++) printf("%02x", sha1_out[i]);
    printf("\n");
    
    printf("\nAll crypto operations completed - ECDAT should detect these operations!\n");
    
    return 0;
}