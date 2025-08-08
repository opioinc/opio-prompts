# FastAPI Security Guidelines (2025)

## Authentication Fundamentals
- Prefer OIDC/OAuth2 providers where possible; fall back to local auth when required.
- Use Argon2id (preferred) or bcrypt via `passlib` for password hashing. Calibrate cost to your hardware.
- Keep access tokens short-lived (5–15 minutes). Use refresh tokens for session continuity.
- Use `OAuth2PasswordBearer` only for local token flows; for OIDC, verify ID/access tokens against issuer and JWKS.
- Store `SECRET_KEY`/private keys in a secret manager. Never in code or plain `.env`.
- Prefer asymmetric JWT signing (RS256/ES256) with JWKS, include `kid`, and rotate keys.

## Password Security
- Minimum length 12; require character diversity or use a password strength estimator (zxcvbn) with high threshold.
- Use `CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")`.
- Implement progressive delays or IP/account throttling for failed logins.
- Provide secure password reset with time-bound, single-use tokens.
- Avoid mandatory periodic rotation for user passwords unless regulation demands it; enforce rotation for credentials/keys.

## Token Best Practices
- Include standard claims: `iss`, `aud`, `sub`, `exp`, `iat`, `nbf`, `jti`.
- Scope tokens minimally; include permissions/roles if needed.
- Validate signature, expiration, audience, and issuer on every request.
- Support token revocation via short-lived access + rotating refresh tokens, or maintain a `jti` denylist for critical revocations.
- For OIDC, fetch and cache JWKS with TTL; respect `kid` changes.

## Authorization Patterns
- Apply least privilege with role/permission checks via dependencies (`Depends`).
- For complex policies, use policy objects or ABAC/RBAC libraries; keep rules in one place.
- Always verify resource ownership on modifying endpoints.

## CORS & Host Protection
- In production, set explicit `allow_origins` (no `*` if credentials). Limit methods/headers to what’s required.
- Use `TrustedHostMiddleware` with your allowed hostnames.
- Set a strict `Content-Security-Policy` for any HTML responses.

## Input Validation & Files
- Validate all inputs with Pydantic. Constrain lengths and patterns.
- For file uploads: validate extensions and MIME types, limit size server-side, and scan for malware when the risk warrants it.
- Store untrusted files outside the web root and randomize filenames.

## SQL Injection & Data Protection
- Use parameterized queries via SQLAlchemy. Never build SQL with string concatenation.
- Protect against mass assignment by explicit schema fields; never blindly map request bodies to ORM models.
- Encrypt sensitive-at-rest data where appropriate (e.g., secrets, tokens, PII segments).

## Rate Limiting & Abuse Protection
- Prefer rate limiting at the gateway or reverse proxy (e.g., Cloudflare, NGINX, API Gateway). Use app-level rate limits for additional protection.
- Use IP/user-based buckets and add stricter limits to auth endpoints.
- Implement exponential backoff for repeated failures.
- Consider device fingerprinting and bot detection for high-risk endpoints.

## Security Headers
- HSTS (`Strict-Transport-Security: max-age=31536000; includeSubDomains`)
- Frameguard (`X-Frame-Options: DENY`) or CSP `frame-ancestors 'none'`.
- MIME sniffing (`X-Content-Type-Options: nosniff`).
- Referrer Policy (`Referrer-Policy: no-referrer` or `strict-origin-when-cross-origin`).
- Permissions Policy to disable unused features.
- Strong `Content-Security-Policy` when serving HTML.

## API Keys
- Prefer user-scoped tokens over static API keys. If using API keys:
  - Generate with `secrets.token_urlsafe(32)`, store hashed, and allow rotation and expiry.
  - Associate scopes and usage analytics; support per-user multiple keys.
  - Restrict by IP or allow-list when viable.

## Session Management (Cookies)
- Use `Secure`, `HttpOnly`, and `SameSite` appropriately. Prefer `SameSite=Lax` or `Strict` for non-OIDC flows.
- Regenerate session IDs on privilege changes and login.
- Set short idle timeouts and absolute session lifetimes for sensitive apps.

## Secrets & Key Management
- Use a secret manager (AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault). Avoid long-lived plaintext secrets.
- Rotate credentials regularly and on incident. Version and audit access to secrets.

## Monitoring & Incident Response
- Log auth and authorization events with correlation IDs. Avoid sensitive payloads in logs.
- Integrate dependency vulnerability scanning in CI (pip-audit, Safety) and runtime alerts.
- Run periodic security tests: SAST in CI, DAST in staging, and targeted penetration tests.
- Maintain incident runbooks, on-call contacts, and breach notification procedures.

## HTTPS/TLS
- Enforce HTTPS end-to-end in production. Use TLS 1.2+ (prefer 1.3) and strong ciphers.
- Automate certificate provisioning/renewal (e.g., Let’s Encrypt) at the proxy.

## Testing Security
- Unit test password hashing, token generation/validation, and permission checks.
- Add abuse tests (login throttling, rate limits) and invalid input fuzzing.
- Verify headers (CORS, CSP, HSTS) on protected endpoints.