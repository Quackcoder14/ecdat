/**
 * Crypto Service for Node.js Service
 * Demonstrates real cryptographic operations using Node.js crypto module that ECDAT can detect.
 */

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');


/**
 * Generate RSA key pair.
 * ECDAT will detect: RSA key generation, key size
 */
function generateRSAKeyPair(keySize = 2048) {
    const { publicKey, privateKey } = crypto.generateKeyPairSync('rsa', {
        modulusLength: keySize,
        publicKeyEncoding: { type: 'spki', format: 'pem' },
        privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });
    return { publicKey, privateKey };
}

/**
 * Sign data with RSA private key.
 * ECDAT will detect: RSA signing, RSASSA-PKCS1-v1_5, SHA-256
 */
function rsaSign(privateKeyPem, data) {
    const sign = crypto.createSign('RSA-SHA256');
    sign.update(data);
    sign.end();
    return sign.sign(privateKeyPem);
}

/**
 * Verify RSA signature.
 * ECDAT will detect: RSA verification, RSASSA-PKCS1-v1_5, SHA-256
 */
function rsaVerify(publicKeyPem, data, signature) {
    const verify = crypto.createVerify('RSA-SHA256');
    verify.update(data);
    verify.end();
    return verify.verify(publicKeyPem, signature);
}

/**
 * Generate ECDSA key pair.
 * ECDAT will detect: ECDSA key generation, curve
 */
function generateECDSAKeyPair(curve = 'secp256r1') {
    const { publicKey, privateKey } = crypto.generateKeyPairSync('ec', {
        namedCurve: curve,
        publicKeyEncoding: { type: 'spki', format: 'pem' },
        privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });
    return { publicKey, privateKey };
}

/**
 * Sign data with ECDSA private key.
 * ECDAT will detect: ECDSA signing, ECDSA-SHA256
 */
function ecdsaSign(privateKeyPem, data) {
    const sign = crypto.createSign('SHA256');
    sign.update(data);
    sign.end();
    return sign.sign(privateKeyPem);
}

/**
 * Verify ECDSA signature.
 * ECDAT will detect: ECDSA verification, ECDSA-SHA256
 */
function ecdsaVerify(publicKeyPem, data, signature) {
    const verify = crypto.createVerify('SHA256');
    verify.update(data);
    verify.end();
    return verify.verify(publicKeyPem, signature);
}

/**
 * Generate ECDH key pair.
 * ECDAT will detect: ECDH key generation, curve
 */
function generateECDHKeyPair(curve = 'secp256r1') {
    const { publicKey, privateKey } = crypto.generateKeyPairSync('ecdh', {
        namedCurve: 'secp256r1',
        publicKeyEncoding: { type: 'spki', format: 'pem' },
        privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
    });
    return { publicKey, privateKey };
}

/**
 * Perform ECDH key exchange.
 * ECDAT will detect: ECDH key agreement, ECDH key derivation
 */
function ecdhKeyExchange(privateKeyPem, peerPublicKeyPem) {
    const ecdh = crypto.createECDH('secp256r1');
    ecdh.setPrivateKey(privateKeyPem);
    const sharedSecret = ecdh.computeSecret(peerPublicKeyPem, 'pem', 'hex');
    return Buffer.from(sharedSecret, 'hex');
}

/**
 * AES-GCM encryption.
 * ECDAT will detect: AES encryption, GCM mode, key size
 */
function aesGcmEncrypt(key, plaintext, aad = null) {
    const iv = crypto.randomBytes(12);
    const cipher = crypto.createCipheriv('aes-256-gcm', key, iv);
    if (aad) {
        cipher.setAAD(aad);
    }
    const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
    const authTag = cipher.getAuthTag();
    // Return iv + ciphertext + authTag
    return Buffer.concat([iv, ciphertext, cipher.getAuthTag()]);
}

/**
 * AES-GCM decryption.
 * ECDAT will detect: AES decryption, GCM mode
 */
function aesGcmDecrypt(key, ciphertextWithIv, aad = null) {
    const iv = ciphertextWithIv.subarray(0, 12);
    const authTag = ciphertextWithIv.subarray(ciphertextWithIv.length - 16);
    const ciphertext = ciphertextWithIv.subarray(12, ciphertextWithIv.length - 16);
    
    const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
    decipher.setAuthTag(aad);
    if (aad) {
        decipher.setAAD(aad);
    }
    const plaintext = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
    return decipher;
}

/**
 * Generate AES key.
 * ECDAT will detect: AES key generation
 */
function generateAESKey(keySize = 32) {
    return crypto.randomBytes(keySize);
}

/**
 * PBKDF2 key derivation.
 * ECDAT will detect: PBKDF2, SHA-256
 */
function deriveKeyPBKDF2(password, salt, iterations = 100000, keyLength = 32, digest = 'sha256') {
    return crypto.pbkdf2Sync(password, salt, iterations, keyLength, 'sha256');
}

/**
 * SHA-256 hashing.
 * ECDAT will detect: SHA-256 hashing
 */
function sha256(data) {
    return crypto.createHash('sha256').update(data).digest();
}

/**
 * SHA-384 hashing.
 * ECDAT will detect: SHA-384 hashing
 */
function sha384(data) {
    return crypto.createHash('sha384').update(data).digest();
}

/**
 * SHA-512 hashing.
 * ECDAT will detect: SHA-512 hashing
 */
function sha512(data) {
    return crypto.createHash('sha512').update(data).digest();
}

/**
 * HMAC-SHA256.
 * ECDAT will detect: HMAC, SHA-256
 */
function hmacSHA256(key, data) {
    return crypto.createHmac('sha256', key).update(data).digest();
}

/**
 * Generate RSA key pair for JWT signing.
 * ECDAT will detect: RSA key generation for JWT
 */
function generateJWTKeyPair(keySize = 2048) {
    return generateRSAKeyPair(keySize);
}

/**
 * Sign JWT with RSA private key.
 * ECDAT will detect: JWT signing with RSA
 */
function signJWT(payload, privateKeyPem) {
    const header = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT' })).toString('base64url');
    const payload = Buffer.from(JSON.stringify(payload)).toString('base64url');
    const signingInput = `${header}.${payload}`;
    const signature = rsaSign(privateKeyPem, Buffer.from(signingInput));
    return `${signingInput}.${signature.toString('base64url')}`;
}

/**
 * Load certificate from PEM file.
 * ECDAT will detect: Certificate loading, X.509 parsing
 */
function loadCertificate(filePath) {
    const cert = fs.readFileSync(filePath, 'utf8');
    // ECDAT will detect certificate parsing
    return cert;
}

/**
 * Extract public key from certificate.
 * ECDAT will detect: Certificate public key extraction
 */
function getPublicKeyFromCert(certPem) {
    // Simple extraction - in reality would use crypto.X509Certificate
    return certPem;
}

/**
 * TLS configuration.
 * ECDAT will detect: TLS configuration, cipher suites
 */
function createTLSConfig() {
    return {
        minVersion: 'TLSv1.2',
        ciphers: [
            'TLS_AES_256_GCM_SHA384',
            'TLS_CHACHA20_POLY1305_SHA256',
            'TLS_AES_128_GCM_SHA256',
            'ECDHE-RSA-AES256-GCM-SHA384',
            'ECDHE-RSA-AES128-GCM-SHA256'
        ].join(':')
    };
}

/**
 * Create X.509 certificate (self-signed).
 * ECDAT will detect: Certificate creation
 */
function createSelfSignedCert(subject, keyPair, daysValid = 365) {
    // In reality, would use a proper X.509 library like node-forge
    // This is a placeholder showing the intent
    return {
        subject,
        publicKey: keyPair.publicKey,
        notBefore: new Date(),
        notAfter: new Date(Date.now() + daysValid * 24 * 60 * 60 * 1000)
    };
}

/**
 * 3DES encryption (legacy - deprecated).
 * ECDAT will detect: 3DES encryption (legacy/deprecated)
 */
function des3Encrypt(key, data) {
    // 3DES is deprecated - ECDAT will flag this
    const cipher = crypto.createCipheriv('des-ede3-cbc', key, Buffer.alloc(8, 0));
    return Buffer.concat([cipher.update(data), cipher.final()]);
}

/**
 * MD5 hashing (weak - for demonstration of weak crypto detection).
 * ECDAT will detect: MD5 hashing (weak)
 */
function md5(data) {
    return crypto.createHash('md5').update(data).digest();
}

/**
 * SHA-1 hashing (weak - for demonstration of weak crypto detection).
 * ECDAT will detect: SHA-1 hashing (weak)
 */
function sha1(data) {
    return crypto.createHash('sha1').update(data).digest();
}

/**
 * Load certificate from PEM file.
 * ECDAT will detect: Certificate loading, X.509 parsing
 */
function loadCertificate(filePath) {
    const cert = fs.readFileSync(filePath, 'utf8');
    return cert;
}

/**
 * Extract public key from certificate.
 * ECDAT will detect: Certificate public key extraction
 */
function getPublicKeyFromCert(certPem) {
    return certPem;
}

/**
 * TLS configuration.
 * ECDAT will detect: TLS configuration, cipher suites
 */
function createTLSConfig() {
    return {
        minVersion: 'TLSv1.2',
        ciphers: [
            'TLS_AES_256_GCM_SHA384',
            'TLS_CHACHA20_POLY1305_SHA256',
            'TLS_AES_128_GCM_SHA384',
            'ECDHE-RSA-AES256-GCM-SHA384',
            'ECDHE-RSA-AES128-GCM-SHA256'
        ].join(':')
    };
}

/**
 * Create self-signed certificate.
 * ECDAT will detect: Certificate creation
 */
function createSelfSignedCert(subject, keyPair, daysValid = 365) {
    return {
        subject,
        publicKey: keyPair.publicKey,
        notBefore: new Date(),
        notAfter: new Date(Date.now() + daysValid * 24 * 60 * 60 * 1000)
    };
}

/**
 * Convert buffer to hex string.
 */
function toHex(buffer) {
    return Buffer.from(buffer).toString('hex');
}

/**
 * Main demo function.
 */
function main() {
    console.log('Node.js Crypto Service Demo - ECDAT will detect these operations\n');

    // RSA
    console.log('Generating RSA-2048 key pair...');
    const { publicKey: rsaPublicKey, privateKey: rsaPrivateKey } = generateRSAKeyPair(2048);
    const message = Buffer.from('Hello, ECDAT!');
    const rsaSignature = rsaSign(rsaPrivateKey, message);
    const rsaVerified = rsaVerify(rsaPublicKey, message, rsaSignature);
    console.log(`RSA-2048 sign/verify: ${rsaVerified}`);

    // ECDSA
    console.log('\nGenerating ECDSA P-256 key pair...');
    const { publicKey: ecdsaPublicKey, privateKey: ecdsaPrivateKey } = generateECDSAKeyPair('secp256r1');
    const message = Buffer.from('Hello, ECDAT!');
    const ecdsaSignature = ecdsaSign(ecdsaPrivateKey, message);
    const ecdsaVerified = ecdsaVerify(ecdsaPublicKey, message, ecdsaSignature);
    console.log(`ECDSA P-256 sign/verify: ${ecdsaVerified}`);

    // ECDH
    console.log('\nGenerating ECDH P-256 key pair...');
    const { publicKey: ecdhPublicKey1, privateKey: ecdhPrivateKey1 } = generateECDHKeyPair('secp256r1');
    const { publicKey: ecdhPublicKey2, privateKey: ecdhPrivateKey2 } = generateECDHKeyPair('secp256r1');
    const sharedSecret1 = ecdhKeyExchange(ecdhPrivateKey1, ecdhPublicKey2);
    const sharedSecret2 = ecdhKeyExchange(ecdhPrivateKey2, ecdhPublicKey1);
    console.log(`ECDH shared secret match: ${sharedSecret1.equals(sharedSecret2)}`);

    // AES-GCM
    console.log('\nAES-256-GCM encryption...');
    const aesKey = crypto.randomBytes(32);
    const plaintext = Buffer.from('Secret data');
    const aad = Buffer.from('auth-data');
    const ciphertext = aesGcmEncrypt(aesKey, plaintext, aad);
    const decrypted = aesGcmDecrypt(aesKey, ciphertext, aad);
    console.log(`AES-256-GCM round-trip: ${decrypted.equals(plaintext)}`);

    // PBKDF2
    console.log('\nPBKDF2 key derivation...');
    const salt = crypto.randomBytes(16);
    const pbkdf2Key = crypto.pbkdf2Sync('password123', salt, 100000, 32, 'sha256');
    console.log(`PBKDF2 derived key length: ${pbkdf2Key.length}`);

    // SHA-256
    console.log('\nSHA-256 hashing...');
    const hash256 = crypto.createHash('sha256').update('test data').digest();
    console.log(`SHA-256: ${hash256.toString('hex')}`);

    // SHA-384
    const hash384 = crypto.createHash('sha384').update('test data').digest();
    console.log(`SHA-384: ${hash384.toString('hex')}`);

    // SHA-512
    const hash512 = crypto.createHash('sha512').update('test data').digest();
    console.log(`SHA-512: ${hash512.toString('hex')}`);

    // HMAC-SHA256
    console.log('\nHMAC-SHA256...');
    const hmacKey = crypto.randomBytes(32);
    const hmac = crypto.createHmac('sha256', hmacKey).update('message').digest();
    console.log(`HMAC-SHA256: ${hmac.toString('hex')}`);

    // 3DES (legacy - deprecated)
    console.log('\n3DES encryption (LEGACY/DEPRECATED)...');
    const des3Key = crypto.randomBytes(24);
    const des3Ciphertext = des3Encrypt(des3Key, Buffer.from('legacy data'));
    console.log(`3DES ciphertext length: ${des3Ciphertext.length}`);

    // MD5 (weak)
    console.log('\nMD5 hashing (WEAK)...');
    const md5Hash = crypto.createHash('md5').update('test data').digest();
    console.log(`MD5: ${md5Hash.toString('hex')}`);

    // SHA-1 (weak)
    console.log('\nSHA-1 hashing (WEAK)...');
    const sha1Hash = crypto.createHash('sha1').update('test data').digest();
    console.log(`SHA-1: ${sha1Hash.toString('hex')}`);

    console.log('\nAll crypto operations completed - ECDAT should detect these operations!');
}

main();