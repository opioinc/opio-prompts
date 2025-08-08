# FastAPI Security Guidelines

## Authentication Fundamentals
- Use **JWT tokens** with python-jose for stateless authentication
- Hash passwords with **bcrypt** using passlib.context.CryptContext
- Set **ACCESS_TOKEN_EXPIRE_MINUTES=30** for short-lived access tokens
- Implement **REFRESH_TOKEN_EXPIRE_DAYS=7** for refresh token rotation
- Use **OAuth2PasswordBearer** for token extraction from headers
- Store **SECRET_KEY** as environment variable with 32+ random bytes
- Use **HS256 algorithm** for JWT signing by default
- Implement **token blacklisting** in Redis for logout functionality
- Add **jti (JWT ID)** claim for unique token identification
- Include **token type** claim to differentiate access/refresh tokens

## Password Security
- Enforce **minimum 8 characters** password length
- Require **at least one uppercase, lowercase, digit, and special character**
- Use **CryptContext(schemes=["bcrypt"], deprecated="auto")**
- Set **bcrypt rounds=12** for adequate security/performance balance
- Implement **password history** to prevent reuse of recent passwords
- Add **password expiry** policy for sensitive applications
- Use **zxcvbn** or similar for password strength validation
- Implement **account lockout** after 5 failed login attempts
- Add **progressive delays** between failed login attempts
- Send **password reset emails** with time-limited tokens

## JWT Implementation
- Include **user_id** in token subject (sub) claim
- Add **exp** claim for token expiration timestamp
- Include **iat** (issued at) for token age validation
- Add **role/permissions** in token claims for authorization
- Implement **token refresh** endpoint for seamless authentication
- Validate **token signature** before processing claims
- Check **token expiration** with timezone-aware datetime
- Handle **JWTError** exceptions with appropriate HTTP responses
- Use **different secrets** for access and refresh tokens
- Implement **token revocation** with Redis blacklist

## Authorization Patterns
- Implement **Role-Based Access Control (RBAC)** with enum roles
- Create **permission-based** authorization for fine-grained control
- Use **Depends()** for reusable authorization dependencies
- Implement **scope-based** permissions for OAuth2 compliance
- Create **@require_role** decorator for route protection
- Check **resource ownership** before allowing modifications
- Implement **hierarchical roles** (admin > moderator > user)
- Use **policy-based** authorization for complex rules
- Cache **user permissions** in Redis for performance
- Audit **authorization failures** for security monitoring

## CORS Configuration
- Set **specific origins** in production, never use "*"
- Configure **allow_credentials=True** for cookie support
- Specify **allowed methods** explicitly (GET, POST, PUT, DELETE)
- List **allowed headers** including Authorization and Content-Type
- Set **max_age=86400** to cache preflight requests
- Use **different CORS settings** for development and production
- Implement **dynamic CORS** based on request origin when needed
- Add **expose_headers** for custom response headers
- Configure **CORS before** other middleware for proper ordering
- Test **CORS configuration** with browser developer tools

## Input Validation
- Use **Pydantic models** for all request validation
- Apply **Field constraints** (min_length, max_length, regex)
- Implement **custom validators** with @field_validator
- Sanitize **HTML input** with bleach or similar library
- Validate **file uploads** by extension and MIME type
- Set **maximum file size** limits (e.g., 5MB)
- Use **EmailStr** for email validation
- Apply **HttpUrl** for URL validation
- Implement **rate limiting** on validation-heavy endpoints
- Log **validation failures** for security monitoring

## SQL Injection Prevention
- Always use **parameterized queries** with SQLAlchemy
- Never use **string concatenation** for SQL construction
- Use **ORM methods** instead of raw SQL when possible
- Validate **input types** before database operations
- Escape **special characters** in LIKE queries
- Use **stored procedures** for complex operations
- Apply **least privilege** principle for database users
- Audit **database queries** in development
- Use **query builders** instead of string manipulation
- Test with **SQL injection payloads** in security testing

## XSS Prevention
- Return **JSON responses** with proper Content-Type headers
- Sanitize **user-generated content** before storage
- Use **Content-Security-Policy** headers
- Set **X-Content-Type-Options: nosniff**
- Apply **X-XSS-Protection: 1; mode=block**
- Escape **HTML entities** in template rendering
- Validate **JSON structure** before processing
- Use **httponly cookies** for session management
- Implement **SameSite cookie** attribute
- Avoid **inline JavaScript** in responses

## Rate Limiting
- Use **slowapi** for FastAPI rate limiting
- Set **5 requests per minute** for login endpoints
- Apply **100 requests per minute** for general API endpoints
- Implement **progressive delays** for repeated failures
- Use **Redis** for distributed rate limit storage
- Apply **different limits** for authenticated vs anonymous users
- Implement **IP-based** and **user-based** rate limiting
- Add **X-RateLimit headers** in responses
- Configure **burst allowance** for temporary spikes
- Implement **circuit breakers** for downstream services

## Security Headers
- Set **Strict-Transport-Security** for HTTPS enforcement
- Add **X-Frame-Options: DENY** to prevent clickjacking
- Include **X-Content-Type-Options: nosniff**
- Set **Referrer-Policy: strict-origin-when-cross-origin**
- Add **Permissions-Policy** for feature restrictions
- Implement **Content-Security-Policy** with strict rules
- Use **middleware** to apply headers globally
- Configure **HSTS max-age=31536000** with includeSubDomains
- Add **X-Request-ID** for request tracing
- Remove **Server header** to hide technology stack

## API Key Management
- Generate **API keys** with secrets.token_urlsafe(32)
- Store **hashed API keys** in database
- Implement **API key rotation** mechanism
- Set **expiration dates** for API keys
- Track **API key usage** for rate limiting
- Support **multiple API keys** per user
- Implement **IP whitelisting** for API keys
- Add **scopes/permissions** to API keys
- Log **API key usage** for auditing
- Provide **secure API key** delivery mechanism

## File Upload Security
- Validate **file extensions** against whitelist
- Check **MIME types** with python-magic
- Implement **virus scanning** with ClamAV or similar
- Store files **outside web root** directory
- Generate **random filenames** to prevent enumeration
- Set **maximum file size** limits
- Use **separate domain** for user content
- Implement **file type conversion** for safety
- Add **rate limiting** for upload endpoints
- Scan for **malicious content** in archives

## Session Management
- Use **secure, httpOnly, sameSite** cookie attributes
- Implement **session timeout** after inactivity
- Generate **cryptographically secure** session IDs
- Store sessions in **Redis** with TTL
- Implement **concurrent session** limiting
- Add **session fingerprinting** for security
- Log **session events** (login, logout, timeout)
- Implement **remember me** with separate token
- Clear **session data** on logout
- Rotate **session IDs** on privilege changes

## Secrets Management
- Store secrets in **environment variables**
- Use **.env files** only in development
- Never commit **secrets to version control**
- Use **AWS Secrets Manager** or HashiCorp Vault in production
- Rotate **secrets regularly**
- Implement **secret versioning**
- Use **different secrets** per environment
- Encrypt **secrets at rest**
- Audit **secret access**
- Implement **emergency secret** rotation procedures

## Security Monitoring
- Log **authentication events** (login, logout, failed attempts)
- Track **authorization failures**
- Monitor **rate limit violations**
- Log **suspicious patterns** (e.g., enumeration attempts)
- Implement **intrusion detection** rules
- Set up **security alerts** for critical events
- Use **centralized logging** with ELK stack or similar
- Implement **audit trails** for sensitive operations
- Monitor **dependency vulnerabilities** with tools like Safety
- Conduct **regular security audits**

## HTTPS/TLS Configuration
- Use **TLS 1.2 minimum**, prefer TLS 1.3
- Implement **strong cipher suites**
- Use **4096-bit RSA** or ECDSA certificates
- Enable **OCSP stapling** for performance
- Implement **certificate pinning** for mobile apps
- Use **Let's Encrypt** for free certificates
- Configure **automatic certificate** renewal
- Redirect **HTTP to HTTPS** automatically
- Test with **SSL Labs** for configuration validation
- Monitor **certificate expiration**

## OAuth2 Implementation
- Support **authorization code flow** for web apps
- Implement **PKCE** for public clients
- Use **state parameter** to prevent CSRF
- Validate **redirect URIs** against whitelist
- Implement **token introspection** endpoint
- Support **token revocation** endpoint
- Use **short-lived tokens** with refresh capability
- Implement **consent management**
- Log **OAuth2 events** for auditing
- Support **multiple OAuth2 providers**

## Security Testing
- Run **SAST** (Static Application Security Testing) in CI
- Perform **DAST** (Dynamic Application Security Testing) regularly
- Use **dependency scanning** for vulnerable packages
- Implement **penetration testing** quarterly
- Run **OWASP ZAP** for vulnerability scanning
- Test with **Burp Suite** for security assessment
- Use **sqlmap** for SQL injection testing
- Implement **fuzzing** for input validation
- Conduct **code reviews** focusing on security
- Maintain **security test** suite

## Incident Response
- Document **incident response** procedures
- Implement **automated alerting** for security events
- Create **runbooks** for common incidents
- Practice **incident drills** regularly
- Maintain **contact list** for security team
- Implement **data breach** notification procedures
- Create **forensic data** collection process
- Document **lessons learned** from incidents
- Implement **rollback procedures** for compromised systems
- Maintain **security incident** log