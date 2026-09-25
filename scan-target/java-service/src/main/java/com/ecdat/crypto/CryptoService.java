package com.ecdat.crypto;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.SecretKeyFactory;
import java.nio.charset.StandardCharsets;
import java.security.*;
import java.security.spec.*;
import java.util.Base64;
import javax.crypto.spec.IvParameterSpec;
import java.security.cert.CertificateFactory;
import java.security.cert.X509Certificate;
import java.io.FileInputStream;
import java.io.ByteArrayInputStream;
import java.io.File;

/**
 * Crypto Service for Java Service
 * Demonstrates real cryptographic operations using JCA/JCE that ECDAT can detect.
 */
public class CryptoService {

    /**
     * Generate RSA key pair.
     * ECDAT will detect: RSA key generation, key size
     */
    public static KeyPair generateRSAKeyPair(int keySize) throws NoSuchAlgorithmException {
        KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA");
        keyGen.initialize(keySize);
        return keyGen.generateKeyPair();
    }

    /**
     * Sign data with RSA private key.
     * ECDAT will detect: RSA signing, SHA256withRSA
     */
    public static byte[] rsaSign(PrivateKey privateKey, byte[] data) throws Exception {
        Signature signature = Signature.getInstance("SHA256withRSA");
        signature.initSign(privateKey);
        signature.update(data);
        return signature.sign();
    }

    /**
     * Verify RSA signature.
     * ECDAT will detect: RSA verification, SHA256withRSA
     */
    public static boolean rsaVerify(PublicKey publicKey, byte[] data, byte[] signature) throws Exception {
        Signature signature = Signature.getInstance("SHA256withRSA");
        signature.initVerify(publicKey);
        signature.update(data);
        return signature.verify(signature);
    }

    /**
     * Generate ECDSA key pair.
     * ECDAT will detect: ECDSA key generation, curve
     */
    public static KeyPair generateECDSAKeyPair(String curveName) throws Exception {
        KeyPairGenerator keyGen = KeyPairGenerator.getInstance("EC");
        ECGenParameterSpec ecSpec = new ECGenParameterSpec(curveName);
        keyGen.initialize(ecSpec);
        return keyGen.generateKeyPair();
    }

    /**
     * Sign data with ECDSA private key.
     * ECDAT will detect: ECDSA signing, SHA256withECDSA
     */
    public static byte[] ecdsaSign(PrivateKey privateKey, byte[] data) throws Exception {
        Signature signature = Signature.getInstance("SHA256withECDSA");
        signature.initSign(privateKey);
        signature.update(data);
        return signature.sign();
    }

    /**
     * Verify ECDSA signature.
     * ECDAT will detect: ECDSA verification, SHA256withECDSA
     */
    public static boolean ecdsaVerify(PublicKey publicKey, byte[] data, byte[] signature) throws Exception {
        Signature signature = Signature.getInstance("SHA256withECDSA");
        signature.initVerify(publicKey);
        signature.update(data);
        return signature.verify(signature);
    }

    /**
     * Generate ECDH key pair.
     * ECDAT will detect: ECDH key generation, curve
     */
    public static KeyPair generateECDHKeyPair(String curveName) throws Exception {
        KeyPairGenerator keyGen = KeyPairGenerator.getInstance("EC");
        ECGenParameterSpec ecSpec = new ECGenParameterSpec(curveName);
        keyGen.initialize(ecSpec);
        return keyGen.generateKeyPair();
    }

    /**
     * Perform ECDH key agreement.
     * ECDAT will detect: ECDH key agreement
     */
    public static byte[] ecdhKeyAgreement(PrivateKey privateKey, PublicKey publicKey) throws Exception {
        KeyAgreement ka = KeyAgreement.getInstance("ECDH");
        ka.init(privateKey);
        ka.doPhase(publicKey, true);
        return ka.generateSecret();
    }

    /**
     * AES-GCM encryption.
     * ECDAT will detect: AES encryption, GCM mode, key size
     */
    public static byte[] aesGcmEncrypt(byte[] key, byte[] plaintext, byte[] aad) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        SecretKey secretKey = new SecretKeySpec(key, "AES");
        byte[] iv = new byte[12];
        SecureRandom random = new SecureRandom();
        random.nextBytes(iv);
        GCMParameterSpec spec = new GCMParameterSpec(128, iv);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, secretKey, spec);
        if (aad != null) {
            cipher.updateAAD(aad);
        }
        byte[] ciphertext = cipher.doFinal(plaintext);
        // Prepend IV to ciphertext
        byte[] result = new byte[iv.length + ciphertext.length];
        System.arraycopy(iv, 0, result, 0, iv.length);
        System.arraycopy(ciphertext, 0, result, iv.length, ciphertext.length);
        return result;
    }

    /**
     * AES-GCM decryption.
     * ECDAT will detect: AES decryption, GCM mode
     */
    public static byte[] aesGcmDecrypt(byte[] key, byte[] ciphertextWithIv, byte[] aad) throws Exception {
        byte[] iv = new byte[12];
        System.arraycopy(ciphertextWithIv, 0, iv, 0, iv.length);
        byte[] ciphertext = new byte[ciphertextWithIv.length - iv.length];
        System.arraycopy(ciphertextWithIv, iv.length, ciphertext, 0, ciphertext.length);
        
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        SecretKey secretKey = new SecretKeySpec(key, "AES");
        GCMParameterSpec spec = new GCMParameterSpec(128, iv);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(key, "AES"), spec);
        if (aad != null) {
            cipher.updateAAD(aad);
        }
        return cipher.doFinal(ciphertext);
    }

    /**
     * Generate AES key.
     * ECDAT will detect: AES key generation
     */
    public static SecretKey generateAESKey(int keySize) throws NoSuchAlgorithmException {
        KeyGenerator keyGen = KeyGenerator.getInstance("AES");
        keyGen.init(keySize);
        return keyGen.generateKey();
    }

    /**
     * PBKDF2 key derivation.
     * ECDAT will detect: PBKDF2, PBKDF2WithHmacSHA256
     */
    public static SecretKey deriveKeyPBKDF2(char[] password, byte[] salt, int iterations, int keyLength) throws Exception {
        PBEKeySpec spec = new PBEKeySpec(password, salt, iterations, keyLength);
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");
        SecretKey tmp = factory.generateSecret(spec);
        return new SecretKeySpec(tmp.getEncoded(), "AES");
    }

    /**
     * SHA-256 hashing.
     * ECDAT will detect: SHA-256 hashing
     */
    public static byte[] sha256(byte[] data) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        return md.digest(data);
    }

    /**
     * SHA-384 hashing.
     * ECDAT will detect: SHA-384 hashing
     */
    public static byte[] sha384(byte[] data) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("SHA-384");
        return md.digest(data);
    }

    /**
     * HMAC-SHA256.
     * ECDAT will detect: HMAC-SHA256
     */
    public static byte[] hmacSHA256(byte[] key, byte[] data) throws Exception {
        Mac mac = Mac.getInstance("HmacSHA256");
        SecretKeySpec keySpec = new SecretKeySpec(key, "HmacSHA256");
        mac.init(keySpec);
        return mac.doFinal(data);
    }

    /**
     * Load certificate from PEM file.
     * ECDAT will detect: Certificate loading, X.509 parsing
     */
    public static X509Certificate loadCertificate(String filePath) throws Exception {
        CertificateFactory cf = CertificateFactory.getInstance("X.509");
        try (FileInputStream fis = new FileInputStream(filePath)) {
            return (X509Certificate) cf.generateCertificate(fis);
        }
    }

    /**
     * Extract public key from certificate.
     * ECDAT will detect: Certificate public key extraction
     */
    public static PublicKey getPublicKeyFromCertificate(X509Certificate cert) {
        return cert.getPublicKey();
    }

    /**
     * TLS configuration using JSSE.
     * ECDAT will detect: TLS configuration, cipher suites
     */
    public static SSLContext createTLSContext() throws Exception {
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, null, new SecureRandom());
        return sslContext;
    }

    /**
     * Generate RSA key pair for JWT signing.
     * ECDAT will detect: RSA key generation for JWT
     */
    public static KeyPair generateJWTKeyPair(int keySize) throws NoSuchAlgorithmException {
        KeyPairGenerator keyGen = KeyPairGenerator.getInstance("RSA");
        keyGen.initialize(keySize);
        return keyGen.generateKeyPair();
    }

    /**
     * 3DES encryption (legacy - for demonstration of legacy crypto detection).
     * ECDAT will detect: 3DES encryption (legacy/deprecated)
     */
    @Deprecated
    public static byte[] des3Encrypt(byte[] key, byte[] data) throws Exception {
        Cipher cipher = Cipher.getInstance("DESede/CBC/PKCS5Padding");
        SecretKeySpec keySpec = new SecretKeySpec(key, "DESede");
        IvParameterSpec iv = new IvParameterSpec(new byte[8]);
        cipher.init(Cipher.ENCRYPT_MODE, keySpec, iv);
        return cipher.doFinal(data);
    }

    public static void main(String[] args) throws Exception {
        System.out.println("Java Crypto Service Demo - ECDAT will detect these operations\n");

        // RSA
        System.out.println("Generating RSA-2048 key pair...");
        KeyPair rsaKeys = generateRSAKeyPair(2048);
        byte[] data = "Hello, ECDAT!".getBytes(StandardCharsets.UTF_8);
        byte[] rsaSig = rsaSign(rsaKeys.getPrivate(), data);
        boolean rsaVerified = rsaVerify(rsaKeys.getPublic(), data, rsaSig);
        System.out.println("RSA-2048 sign/verify: " + rsaVerified);

        // ECDSA
        System.out.println("\nGenerating ECDSA P-256 key pair...");
        KeyPair ecdsaKeys = generateECDSAKeyPair("secp256r1");
        byte[] ecdsaSig = ecdsaSign(ecdsaKeys.getPrivate(), "Hello, ECDAT!".getBytes());
        boolean ecdsaVerified = ecdsaVerify(ecdsaKeys.getPublic(), "Hello, ECDAT!".getBytes(), ecdsaSig);
        System.out.println("ECDSA P-256 sign/verify: " + ecdsaVerified);

        // ECDH
        System.out.println("\nGenerating ECDH P-256 key pair...");
        KeyPair ecdhKeys1 = generateECDHKeyPair("secp256r1");
        KeyPair ecdhKeys2 = generateECDHKeyPair("secp256r1");
        byte[] shared1 = ecdhKeyAgreement(ecdhKeys1.getPrivate(), ecdhKeys2.getPublic());
        byte[] shared2 = ecdhKeyAgreement(ecdhKeys2.getPrivate(), ecdhKeys1.getPublic());
        System.out.println("ECDH shared secret match: " + java.util.Arrays.equals(shared1, shared2));

        // AES-GCM
        System.out.println("\nAES-256-GCM encryption...");
        byte[] aesKey = generateAESKey(256).getEncoded();
        byte[] plaintext = "Secret data".getBytes(StandardCharsets.UTF_8);
        byte[] aad = "auth-data".getBytes(StandardCharsets.UTF_8);
        byte[] ciphertext = aesGcmEncrypt(aesKey, plaintext, aad);
        byte[] decrypted = aesGcmDecrypt(aesKey, ciphertext, aad);
        System.out.println("AES-256-GCM round-trip: " + new String(decrypted, StandardCharsets.UTF_8).equals("Secret data"));

        // PBKDF2
        System.out.println("\nPBKDF2 key derivation...");
        byte[] salt = new byte[16];
        new SecureRandom().nextBytes(salt);
        SecretKey pbkdf2Key = deriveKeyPBKDF2("password123".toCharArray(), salt, 100000, 256);
        System.out.println("PBKDF2 derived key length: " + pbkdf2Key.getEncoded().length);

        // SHA-256
        System.out.println("\nSHA-256 hashing...");
        byte[] hash = sha256("test data".getBytes(StandardCharsets.UTF_8));
        System.out.println("SHA-256: " + bytesToHex(hash));

        // SHA-384
        byte[] hash384 = sha384("test data".getBytes(StandardCharsets.UTF_8));
        System.out.println("SHA-384: " + bytesToHex(hash384));

        // HMAC-SHA256
        System.out.println("\nHMAC-SHA256...");
        byte[] hmacKey = new byte[32];
        new SecureRandom().nextBytes(hmacKey);
        byte[] hmac = hmacSHA256(hmacKey, "message".getBytes(StandardCharsets.UTF_8));
        System.out.println("HMAC-SHA256: " + bytesToHex(hmac));

        // 3DES (legacy - deprecated)
        System.out.println("\n3DES encryption (LEGACY/DEPRECATED)...");
        byte[] des3Key = new byte[24]; // 192 bits for 3DES
        new SecureRandom().nextBytes(des3Key);
        byte[] des3Ciphertext = des3Encrypt(des3Key, "legacy data".getBytes(StandardCharsets.UTF_8));
        System.out.println("3DES ciphertext length: " + des3Ciphertext.length);

        System.out.println("\nAll crypto operations completed - ECDAT should detect these operations!");
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}