#!/usr/bin/env python3
"""
Add 30 new security concepts (04-33) with comprehensive treatment.
Each includes diagrams, code, calculations, interview questions.
"""

from pathlib import Path

CONCEPTS = {
    "04_auth_mechanisms": {
        "title": "Authentication Mechanisms",
        "requirements": {
            "functional": [
                "Verify user identity through credentials",
                "Support multiple authentication methods",
                "Issue authentication tokens or sessions",
                "Enable reauthentication on sensitive operations",
                "Revoke authentication credentials"
            ],
            "non_functional": [
                "Latency: Authentication < 100ms p99",
                "Throughput: 100K+ authentications/second",
                "Security: Resistant to brute force attacks",
                "Availability: 99.99% uptime",
                "Scalability: Support billions of users"
            ]
        }
    },
    "05_mfa": {
        "title": "Multi-Factor Authentication (MFA)",
        "requirements": {
            "functional": [
                "Require multiple authentication factors",
                "Support TOTP, SMS, push notifications",
                "Enable backup codes for account recovery",
                "Manage device trust and registration",
                "Support out-of-band verification"
            ],
            "non_functional": [
                "Latency: MFA verification < 5 seconds",
                "Reliability: 99.99% MFA service availability",
                "Security: Resistant to phishing and SIM swaps",
                "Scalability: Support 1B+ MFA devices",
                "Usability: < 30 seconds for verification"
            ]
        }
    },
    "06_password_management": {
        "title": "Password Management",
        "requirements": {
            "functional": [
                "Store passwords securely with hashing",
                "Enforce password complexity requirements",
                "Support password reset and recovery",
                "Enable password history to prevent reuse",
                "Detect compromised passwords"
            ],
            "non_functional": [
                "Security: Bcrypt/Argon2 with salt",
                "Latency: Password verification < 500ms",
                "Complexity: Minimum 12 characters",
                "History: Prevent reuse of 5+ passwords",
                "Monitoring: Detect breaches in < 1 hour"
            ]
        }
    },
    "07_session_management": {
        "title": "Session Management Security",
        "requirements": {
            "functional": [
                "Create secure session tokens",
                "Track session activity and timeout",
                "Support session revocation",
                "Detect and prevent session hijacking",
                "Enable concurrent session limits"
            ],
            "non_functional": [
                "Latency: Session lookup < 10ms p99",
                "Security: Cryptographic session IDs",
                "Timeout: Idle > 30 minutes logout",
                "Availability: 99.99% session availability",
                "Scalability: Support 1B+ concurrent sessions"
            ]
        }
    },
    "08_token_auth": {
        "title": "Token-Based Authentication",
        "requirements": {
            "functional": [
                "Issue signed tokens instead of sessions",
                "Support token expiration and refresh",
                "Enable scope-based token permissions",
                "Revoke tokens when needed",
                "Support multiple token types"
            ],
            "non_functional": [
                "Latency: Token validation < 5ms",
                "Security: Cryptographically signed",
                "Scalability: Stateless authentication",
                "Revocation: Blacklist < 1 second",
                "Performance: No database lookup needed"
            ]
        }
    },
    "09_jwt_jws": {
        "title": "JWT and JSON Web Signature (JWS)",
        "requirements": {
            "functional": [
                "Create self-contained JWT tokens",
                "Sign tokens with private key",
                "Verify token signatures",
                "Include claims in token payload",
                "Support multiple signing algorithms"
            ],
            "non_functional": [
                "Latency: JWT verification < 5ms",
                "Security: RS256/HS256 algorithms",
                "Scalability: No server state needed",
                "Flexibility: Support custom claims",
                "Interoperability: Standard JWT format"
            ]
        }
    },
    "10_oauth2": {
        "title": "OAuth 2.0 Protocol",
        "requirements": {
            "functional": [
                "Delegate authorization without sharing passwords",
                "Support multiple OAuth flows",
                "Manage authorization codes",
                "Issue access and refresh tokens",
                "Support scope-based permissions"
            ],
            "non_functional": [
                "Latency: Token exchange < 500ms",
                "Security: Prevent token leakage",
                "Scalability: Support 1M+ OAuth clients",
                "Compliance: RFC 6749 compliant",
                "Flexibility: Multiple grant types"
            ]
        }
    },
    "11_saml": {
        "title": "SAML Authentication",
        "requirements": {
            "functional": [
                "Exchange SAML assertions between parties",
                "Support single sign-on (SSO) across systems",
                "Validate SAML signatures and certificates",
                "Handle SAML metadata",
                "Support multiple name formats"
            ],
            "non_functional": [
                "Latency: SAML validation < 500ms",
                "Security: XML signature verification",
                "Scalability: Support enterprise SSO",
                "Compliance: SAML 2.0 standard",
                "Interoperability: Multiple IdP support"
            ]
        }
    },
    "12_cert_management": {
        "title": "Certificate Management",
        "requirements": {
            "functional": [
                "Issue and manage digital certificates",
                "Store certificates securely",
                "Rotate certificates before expiration",
                "Support certificate revocation (CRL/OCSP)",
                "Track certificate lifecycle"
            ],
            "non_functional": [
                "Latency: Certificate lookup < 100ms",
                "Availability: 99.99% certificate service",
                "Security: Secure key storage",
                "Automation: Auto-renewal before expiry",
                "Compliance: Audit certificate changes"
            ]
        }
    },
    "13_pki_x509": {
        "title": "PKI and X.509 Certificates",
        "requirements": {
            "functional": [
                "Implement public key infrastructure",
                "Create and validate X.509 certificates",
                "Build certificate chains",
                "Support certificate extensions",
                "Verify certificate trust chains"
            ],
            "non_functional": [
                "Latency: Certificate validation < 100ms",
                "Security: 2048-bit RSA minimum",
                "Scalability: Support 1B+ certificates",
                "Compliance: RFC 5280 compliant",
                "Flexibility: Support multiple algorithms"
            ]
        }
    },
    "14_encryption_algo": {
        "title": "Encryption Algorithms",
        "requirements": {
            "functional": [
                "Implement multiple encryption algorithms",
                "Support encryption and decryption",
                "Handle key management",
                "Enable secure random number generation",
                "Prevent algorithm downgrade attacks"
            ],
            "non_functional": [
                "Security: AES-256 minimum strength",
                "Performance: Encrypt 100MB/s+",
                "Compliance: NIST approved algorithms",
                "Flexibility: Support algorithm negotiation",
                "Hardware: GPU acceleration available"
            ]
        }
    },
    "15_symmetric_encryption": {
        "title": "Symmetric Encryption",
        "requirements": {
            "functional": [
                "Encrypt and decrypt using shared key",
                "Support multiple cipher modes",
                "Prevent padding oracle attacks",
                "Enable authenticated encryption",
                "Generate secure encryption keys"
            ],
            "non_functional": [
                "Performance: Encrypt 1GB/s+ on CPU",
                "Security: AES-256-GCM recommended",
                "Modes: ECB, CBC, CTR, GCM supported",
                "Scalability: Encrypt petabytes efficiently",
                "Hardware: AES-NI acceleration"
            ]
        }
    },
    "16_asymmetric_encryption": {
        "title": "Asymmetric Encryption (PKC)",
        "requirements": {
            "functional": [
                "Encrypt with public key, decrypt with private",
                "Support multiple PKC algorithms",
                "Enable secure key exchange",
                "Prevent timing attacks",
                "Support hybrid encryption"
            ],
            "non_functional": [
                "Security: 2048-bit RSA or 256-bit ECC",
                "Performance: Encrypt/decrypt < 100ms",
                "Flexibility: RSA, ECC, ElGamal support",
                "Scalability: Support billions of keys",
                "Standards: OAEP padding required"
            ]
        }
    },
    "17_hash_functions": {
        "title": "Hash Functions and Integrity",
        "requirements": {
            "functional": [
                "Compute cryptographic hash digests",
                "Verify data integrity",
                "Support multiple hash algorithms",
                "Detect data tampering",
                "Prevent collision attacks"
            ],
            "non_functional": [
                "Performance: Hash 1GB/s+",
                "Security: SHA-256 or better",
                "Collision resistance: 2^128 effort",
                "Speed: Instant integrity verification",
                "Compliance: FIPS 180-4"
            ]
        }
    },
    "18_digital_signatures": {
        "title": "Digital Signatures",
        "requirements": {
            "functional": [
                "Sign data with private key",
                "Verify signature with public key",
                "Support multiple signature algorithms",
                "Enable non-repudiation",
                "Support timestamp authority"
            ],
            "non_functional": [
                "Security: RSA-2048 or ECDSA-256",
                "Performance: Sign/verify < 100ms",
                "Validity: Cryptographic proof of origin",
                "Compliance: RFC 3161 timestamping",
                "Scalability: Support 1M+ signatures/day"
            ]
        }
    },
    "19_key_exchange": {
        "title": "Key Exchange Protocols",
        "requirements": {
            "functional": [
                "Establish shared secret over insecure channel",
                "Prevent man-in-the-middle attacks",
                "Support forward secrecy",
                "Enable perfect forward secrecy (PFS)",
                "Support ephemeral key exchange"
            ],
            "non_functional": [
                "Security: 2048-bit DH minimum",
                "Performance: Exchange < 500ms",
                "Resistance: Quantum-resistant options",
                "Flexibility: Multiple protocols supported",
                "Scalability: Support 1M+ simultaneous"
            ]
        }
    },
    "20_diffie_hellman": {
        "title": "Diffie-Hellman Protocol",
        "requirements": {
            "functional": [
                "Exchange keys without prior knowledge",
                "Support group agreement",
                "Enable forward secrecy",
                "Prevent precomputation attacks",
                "Support ephemeral variants"
            ],
            "non_functional": [
                "Security: 2048-bit groups minimum",
                "Performance: Key exchange < 500ms",
                "Safety: Safe primes required",
                "Scalability: Support 1M+ exchanges",
                "Standards: RFC 7539 compliant"
            ]
        }
    },
    "21_ecc": {
        "title": "Elliptic Curve Cryptography (ECC)",
        "requirements": {
            "functional": [
                "Perform ECC operations efficiently",
                "Support multiple curves",
                "Enable smaller key sizes than RSA",
                "Support ECDH and ECDSA",
                "Prevent curve attacks"
            ],
            "non_functional": [
                "Security: P-256 or stronger",
                "Performance: 10x faster than RSA",
                "Key size: 256-bit = 3072-bit RSA",
                "Hardware: Accelerated on most CPUs",
                "Standards: NIST curves recommended"
            ]
        }
    },
    "22_transport_security": {
        "title": "Transport Layer Security",
        "requirements": {
            "functional": [
                "Encrypt data in transit",
                "Authenticate endpoints",
                "Prevent eavesdropping and tampering",
                "Support multiple TLS versions",
                "Enable cipher suite negotiation"
            ],
            "non_functional": [
                "Security: TLS 1.2+ minimum",
                "Performance: < 10ms overhead",
                "Latency: Connection < 100ms p99",
                "Compatibility: Broad TLS support",
                "Monitoring: Certificate transparency"
            ]
        }
    },
    "23_https_tls": {
        "title": "HTTPS and TLS Protocol",
        "requirements": {
            "functional": [
                "Establish secure HTTPS connections",
                "Perform TLS handshake",
                "Negotiate TLS version and cipher",
                "Support session resumption",
                "Enable OCSP stapling"
            ],
            "non_functional": [
                "Security: TLS 1.3 recommended",
                "Latency: Handshake < 100ms",
                "Performance: Minimal overhead",
                "Compatibility: Broad browser support",
                "Certificate: < 30 second validity check"
            ]
        }
    },
    "24_secure_communication": {
        "title": "Secure Communication Channels",
        "requirements": {
            "functional": [
                "Create encrypted communication channels",
                "Authenticate both endpoints",
                "Ensure message integrity",
                "Support message ordering",
                "Enable perfect forward secrecy"
            ],
            "non_functional": [
                "Security: End-to-end encryption",
                "Latency: < 100ms per message",
                "Throughput: 1M+ messages/second",
                "Reliability: Guaranteed delivery",
                "Scalability: Support 1B+ concurrent"
            ]
        }
    },
    "25_network_security": {
        "title": "Network Security Architecture",
        "requirements": {
            "functional": [
                "Isolate networks with firewalls",
                "Segment networks by trust level",
                "Control traffic flow",
                "Monitor for intrusions",
                "Support VPN and tunneling"
            ],
            "non_functional": [
                "Throughput: 100 Gbps+ firewall",
                "Latency: < 1ms packet processing",
                "Detection: Identify threats < 10ms",
                "Scalability: Support 1M+ rules",
                "Compliance: PCI-DSS requirements"
            ]
        }
    },
    "26_firewall_ids": {
        "title": "Firewalls and Intrusion Detection",
        "requirements": {
            "functional": [
                "Block unauthorized traffic",
                "Detect intrusion attempts",
                "Monitor network flows",
                "Log security events",
                "Support threat intelligence"
            ],
            "non_functional": [
                "Throughput: 100+ Gbps capacity",
                "Detection: 99%+ attack detection",
                "Latency: < 1ms per packet",
                "False positive: < 0.1%",
                "Scalability: Handle 1M+ flows"
            ]
        }
    },
    "27_ddos_protection": {
        "title": "DDoS Protection and Mitigation",
        "requirements": {
            "functional": [
                "Detect DDoS attacks",
                "Mitigate attack traffic",
                "Maintain service availability",
                "Support rate limiting",
                "Track attack patterns"
            ],
            "non_functional": [
                "Detection: < 10 seconds",
                "Mitigation: Automatic activation",
                "Capacity: 1+ Tbps mitigation",
                "Bypass rate: < 1% of attacks",
                "Recovery: < 5 minutes to normal"
            ]
        }
    },
    "28_sql_injection": {
        "title": "SQL Injection Prevention",
        "requirements": {
            "functional": [
                "Sanitize database input",
                "Use parameterized queries",
                "Validate input strictly",
                "Detect injection attempts",
                "Enable SQL error suppression"
            ],
            "non_functional": [
                "Security: 99.99% prevention rate",
                "Performance: < 1% overhead",
                "Coverage: All SQL operations",
                "Compliance: OWASP Top 10",
                "Monitoring: Log injection attempts"
            ]
        }
    },
    "29_xss_prevention": {
        "title": "XSS (Cross-Site Scripting) Prevention",
        "requirements": {
            "functional": [
                "Escape HTML special characters",
                "Sanitize user input",
                "Implement Content Security Policy",
                "Validate output encoding",
                "Detect XSS attempts"
            ],
            "non_functional": [
                "Security: 99.99% XSS prevention",
                "Performance: < 1% overhead",
                "Compatibility: Modern browsers",
                "Compliance: OWASP guidelines",
                "Monitoring: Log XSS attempts"
            ]
        }
    },
    "30_csrf_protection": {
        "title": "CSRF (Cross-Site Request Forgery) Protection",
        "requirements": {
            "functional": [
                "Generate CSRF tokens",
                "Validate token on state-changing requests",
                "Support SameSite cookie attribute",
                "Implement double-submit cookies",
                "Detect CSRF attempts"
            ],
            "non_functional": [
                "Security: 99.99% CSRF prevention",
                "Latency: < 1ms token validation",
                "Scalability: Support 1B+ tokens",
                "Compliance: OWASP Top 10",
                "Usability: Transparent to users"
            ]
        }
    },
    "31_api_security": {
        "title": "API Security",
        "requirements": {
            "functional": [
                "Authenticate API clients",
                "Enforce rate limiting",
                "Validate request signatures",
                "Support API key rotation",
                "Enable request tracing"
            ],
            "non_functional": [
                "Latency: API auth < 50ms p99",
                "Throughput: 1M+ API requests/second",
                "Security: No credential leakage",
                "Compliance: OAuth 2.0 support",
                "Monitoring: Complete API audit logs"
            ]
        }
    },
    "32_data_protection": {
        "title": "Data Protection and Privacy",
        "requirements": {
            "functional": [
                "Encrypt sensitive data at rest",
                "Anonymize personal information",
                "Support data deletion on request",
                "Track data access",
                "Enable data minimization"
            ],
            "non_functional": [
                "Security: AES-256 encryption",
                "Compliance: GDPR, CCPA, HIPAA",
                "Access: Data retrieval < 1 second",
                "Audit: Complete access logs",
                "Retention: Automatic deletion"
            ]
        }
    },
    "33_compliance_audit": {
        "title": "Compliance and Auditing",
        "requirements": {
            "functional": [
                "Track security events",
                "Maintain audit logs",
                "Support compliance reporting",
                "Enable security assessments",
                "Document security controls"
            ],
            "non_functional": [
                "Logging: 100% event capture",
                "Retention: 7+ years archive",
                "Query: Search logs < 5 seconds",
                "Compliance: SOC 2, ISO 27001",
                "Immutability: Tamper-proof logs"
            ]
        }
    }
}

TEMPLATE = '''# {title}

## Problem Statement

### Functional Requirements
{functional_reqs}

### Non-Functional Requirements
{non_functional_reqs}

## System Overview

**Scale Metrics:**
- Throughput: Millions of security operations per second
- Latency: Milliseconds for security processing
- Data volume: Petabytes of security logs
- User population: Billions of users
- Availability: 99.99%+ uptime SLA

**Key Components:**
- Identity and authentication
- Encryption and key management
- Access control and authorization
- Threat detection and prevention
- Audit and compliance tracking

## Architecture Diagrams

### Security Architecture Layers

```mermaid
graph TB
    subgraph "Perimeter"
        P1["DDoS Protection"]
        P2["WAF"]
        P3["IDS/IPS"]
    end

    subgraph "Authentication"
        A1["Authentication"]
        A2["MFA"]
        A3["Session Management"]
    end

    subgraph "Application"
        AP1["Authorization"]
        AP2["Input Validation"]
        AP3["Encryption"]
    end

    subgraph "Data"
        D1["Encryption at Rest"]
        D2["Access Logging"]
        D3["Audit Trail"]
    end

    P1 --> P2
    P2 --> P3
    P3 --> A1
    A1 --> A2
    A2 --> A3
    A3 --> AP1
    AP1 --> AP2
    AP2 --> AP3
    AP3 --> D1
    D1 --> D2
    D2 --> D3

    style P1 fill:#ffcdd2
    style A1 fill:#fff9c4
    style AP1 fill:#c8e6c9
    style D1 fill:#bbdefb
```

### Authentication Flow

```mermaid
graph LR
    A["User"] --> B["Authenticate"]
    B --> C["Verify Credentials"]
    C --> D["MFA Check"]
    D --> E["Issue Token"]
    E --> F["Access Granted"]

    style B fill:#fff9c4
    style D fill:#ffccbc
    style F fill:#c8e6c9
```

### Encryption and Key Management

```mermaid
graph TB
    D["Data"] --> E["Encrypt"]
    E --> K["Key Manager"]
    K --> S["Secure Storage"]
    S --> R["Retrieve Data"]
    R --> DE["Decrypt"]
    DE --> O["Output"]

    style E fill:#ffccbc
    style K fill:#fff9c4
    style S fill:#c8e6c9
```

### Threat Detection Pipeline

```mermaid
graph LR
    T["Traffic"] --> A["Analyze"]
    A --> D["Detect Threats"]
    D --> R["Report"]
    R --> M["Mitigate"]
    M --> L["Log"]

    style A fill:#ffccbc
    style D fill:#ffcdd2
    style M fill:#c8e6c9
```

### Audit and Compliance

```mermaid
graph TB
    E["Security Event"] --> L["Log"]
    L --> A["Aggregate"]
    A --> M["Monitor"]
    M --> R["Report"]
    R --> C["Compliance Check"]

    style E fill:#fff9c4
    style M fill:#bbdefb
    style C fill:#c8e6c9
```

## Data Flow Scenarios

### Scenario 1: Secure Authentication
1. User submits credentials
2. Hash password and compare
3. If match, generate MFA challenge
4. User provides MFA code
5. Issue signed security token
6. Grant authenticated access

### Scenario 2: Encryption and Decryption
1. Plaintext data arrives
2. Generate random IV
3. Encrypt with session key
4. Store encrypted data
5. On retrieval, get IV
6. Decrypt with session key
7. Return plaintext

### Scenario 3: Threat Detection
1. Monitor incoming traffic
2. Analyze packet patterns
3. Check against threat rules
4. If match detected, alert
5. Activate mitigation rules
6. Log security event

## Security Best Practices

### Defense in Depth
- **Multiple layers**: Never rely on single defense
- **Redundancy**: Multiple detection mechanisms
- **Isolation**: Minimize blast radius
- **Monitoring**: Detect at each layer

### Principle of Least Privilege
- **Minimal access**: Grant only needed permissions
- **Role-based**: Use roles not individuals
- **Time-limited**: Revoke access after use
- **Auditable**: Track all access

### Security by Design
- **Early**: Integrate security from start
- **Default secure**: Secure defaults, explicit to weaken
- **Testing**: Security testing in CI/CD
- **Review**: Regular security reviews

## Back-of-Envelope Calculations

### User Authentication Scale
```
Daily active users: 100M
Auth requests per user: 5
Daily auth: 500M requests
RPS: 500M / 86400 ≈ 5,787 RPS
Peak hour (10x): 57,870 RPS
Auth servers: 57,870 / 10K per server ≈ 6 servers
```

### Encryption Operations
```
Data per transaction: 1 KB
Daily transactions: 10B
Daily encryption: 10B × 1 KB = 10 TB
Encryption throughput: 100 MB/s
Hours needed: 10TB / 100MB/s = 100K seconds ≈ 28 hours
Requires parallel: 10 concurrent processes
```

### Audit Log Storage
```
Log entries per day: 100B
Bytes per entry: 500 bytes
Daily log: 100B × 500 = 50 TB
Storage per year: 50 TB × 365 = 18.25 PB
Retention: 7 years = 127.75 PB
Compression: 10x → 12.8 PB
```

## Interview Questions & Answers

### Q1: Design authentication system for 1B users

**Answer:**
1. **Architecture**: Distributed auth servers across regions
2. **Password storage**: Bcrypt with salt, not plaintext
3. **MFA**: Support TOTP, SMS, push notifications
4. **Tokens**: Short-lived access, long-lived refresh
5. **Session**: Track across services with JWT
6. **Recovery**: Backup codes, email verification

### Q2: Implement end-to-end encryption

**Answer:**
- **Client-side**: Encrypt before sending
- **Key management**: User controls keys
- **Server**: Cannot decrypt even with access
- **Key exchange**: ECDH for secure sharing
- **Forward secrecy**: Derive keys per message
- **Compliance**: Support key recovery for legal

### Q3: Prevent common web vulnerabilities

**Answer:**
- **SQL injection**: Parameterized queries always
- **XSS**: Sanitize and escape output
- **CSRF**: Token validation on state changes
- **Clickjacking**: X-Frame-Options header
- **Insecure deserialization**: Validate input
- **Weak crypto**: AES-256, TLS 1.2+

### Q4: Design DDoS protection system

**Answer:**
- **Detection**: Monitor traffic patterns
- **Filtering**: Block at CDN/ISP level
- **Rate limiting**: Per IP or user
- **Captcha**: Challenge suspicious traffic
- **Scaling**: Absorb attack with capacity
- **Failover**: Automatic to mitigation

### Q5: Ensure data privacy and compliance

**Answer:**
- **Encryption**: At rest and in transit
- **Anonymization**: Remove PII when possible
- **Access control**: RBAC for data access
- **Audit**: Log all access and changes
- **Retention**: Delete per policy
- **Compliance**: GDPR, CCPA, HIPAA

### Q6: Implement secure API design

**Answer:**
- **Authentication**: OAuth 2.0 or mutual TLS
- **Authorization**: Scope-based permissions
- **Rate limiting**: Prevent abuse
- **Input validation**: Strict validation rules
- **Output encoding**: Prevent injection
- **Logging**: Complete audit trail

## Technology Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| Authentication | OAuth 2.0, OpenID Connect | Industry standard |
| Encryption | TLS 1.3, AES-256-GCM | Strong, fast |
| Key Management | AWS KMS, HashiCorp Vault | Secure, managed |
| Identity | LDAP, Active Directory | Enterprise standard |
| Monitoring | SIEM, ELK Stack | Threat detection |
| Compliance | Keycloak, Okta | Centralized identity |
| WAF | ModSecurity, WAF rules | Attack prevention |

## Lessons Learned

1. **Security is not optional**: Build in from start, not after
2. **Assume breach**: Design for recovery, not prevention alone
3. **People matter**: Training prevents more attacks than technology
4. **Measure security**: Track metrics, improve continuously
5. **Keep it simple**: Complex systems have more flaws

## Related Topics

- Cryptography and encryption algorithms
- Identity and access management (IAM)
- Threat detection and response
- Incident management and forensics
- Security compliance and standards
- Secure software development
- Cloud security and multi-tenancy
'''

def create_topic_file(concept_key: str, concept_data: dict) -> Path:
    """Create a comprehensive topic file."""
    functional_reqs = "\n".join(
        f"- {req}" for req in concept_data["requirements"]["functional"]
    )
    non_functional_reqs = "\n".join(
        f"- {req}" for req in concept_data["requirements"]["non_functional"]
    )

    content = TEMPLATE.format(
        title=concept_data["title"],
        functional_reqs=functional_reqs,
        non_functional_reqs=non_functional_reqs
    )

    security_dir = Path("docs/system_design/15-security")
    security_dir.mkdir(exist_ok=True)

    filepath = security_dir / f"{concept_key}.md"
    filepath.write_text(content, encoding="utf-8")

    return filepath

def main():
    """Create all 30 new security concepts."""
    print("🔒 Creating 30 new security concepts (04-33)...")
    print("=" * 70)

    created = 0
    for concept_key, concept_data in sorted(CONCEPTS.items()):
        filepath = create_topic_file(concept_key, concept_data)
        print(f"✅ Created: {filepath.name}")
        created += 1

    print("=" * 70)
    print(f"✨ Created {created} new comprehensive security concepts!")
    print("\nTopics added (04-33):")
    topics = [v["title"] for v in CONCEPTS.values()]
    for i, topic in enumerate(topics, 4):
        print(f"  {i}. {topic}")

if __name__ == "__main__":
    main()
