# CoachPath Authentication Architecture Specification

## 1. Executive Summary & Philosophy

CoachPath processes sensitive candidate career information—including employment histories, academic credentials, tailored resumes, skill assessments, and salary preferences. To safeguard user identity and preserve data confidentiality, the authentication layer is engineered around zero-trust and defense-in-depth principles:

1. **Zero Secret Exposure**: Passwords and raw refresh tokens are never persisted in plaintext, logged, or returned in API responses.
2. **Dual-Channel Token Delivery**: Credentials are transmitted via modern `HttpOnly`, `SameSite=Lax`, `Secure` browser cookies for seamless cross-site scripting (XSS) defense, while simultaneously returning JSON payload tokens for programmatic, mobile, and non-browser consumers.
3. **Atomic Session Rotation**: Refresh tokens are single-use. Any presentation of a previously consumed refresh token triggers an immediate replay-attack alert and revokes all active sessions for that user account.
4. **Deterministic Rate Limiting**: Authentication routes are guarded by a sliding-window rate limiter (5 failed attempts per 15 minutes) to defeat brute-force and credential-stuffing attacks.

---

## 2. Password Security & Cryptography

### 2.1 Argon2id Hashing Algorithm
All passwords are encrypted using **Argon2id**, the winner of the Password Hashing Competition (PHC) and the gold standard for resisting GPU/ASIC brute-force cracking.

| Parameter | Value | Rationale |
| :--- | :--- | :--- |
| **Algorithm** | Argon2id (`Type.ID`) | Hybrid data-dependent and data-independent memory access resistant to cache-timing attacks |
| **Time Cost** ($t$) | 3 iterations | Adequate computational difficulty without impacting API latency |
| **Memory Cost** ($m$) | 65,536 KiB (64 MiB) | High memory hardness rendering GPU clusters economically unfeasible |
| **Parallelism** ($p$) | 4 threads | Matches modern multi-core server processors |
| **Salt** | Cryptographically random 16 bytes | Automatically generated per-password by `argon2-cffi` |

### 2.2 Complexity Enforcement
Candidate passwords must pass regex validation prior to hashing:
- **Minimum Length**: 8 characters
- **Maximum Length**: 128 characters
- **Uppercase Letter**: $\ge 1$ (`[A-Z]`)
- **Lowercase Letter**: $\ge 1$ (`[a-z]`)
- **Numeric Digit**: $\ge 1$ (`[0-9]`)
- **Special Character**: $\ge 1$ (`[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]`)

Weak passwords return HTTP 422 Unprocessable Content with granular error details.

---

## 3. Token & Session Architecture

### 3.1 Access Tokens (JWT)
- **Standard**: RFC 7519 JSON Web Token
- **Signing Algorithm**: HMAC-SHA256 (`HS256`)
- **Validity Window**: 60 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES = 60`)
- **Token Claims**:
  - `sub`: User ID (`UUID4`)
  - `email`: Normalized email string
  - `role`: Authorization role (`"candidate"` or `"admin"`)
  - `jti`: Unique token identifier (`UUID4`)
  - `iat`: Epoch issue timestamp (`UTC`)
  - `exp`: Epoch expiration timestamp (`UTC`)
- **Verification**: Strictly verified against server `SECRET_KEY`. Any malformed signature or expired timestamp triggers HTTP 401 `AUTHENTICATION_REQUIRED`.

### 3.2 Refresh Tokens (Opaque + SHA-256 Hashed)
- **Entropy**: Cryptographically secure 256-bit random string generated via `secrets.token_urlsafe(32)`.
- **Validity Window**: 7 days (`REFRESH_TOKEN_EXPIRE_DAYS = 7`).
- **Database Storage**: The raw token is **never stored**. Only its SHA-256 cryptographic digest (`hash_token(raw_token)`) is saved in the `user_sessions` PostgreSQL table.
- **Session Metadata**: Stores user agent, IP address, expiration timestamp, and revocation flag (`is_revoked`).

```
Candidate Browser / Client
   │
   │  1. POST /api/v1/auth/login { email, password }
   ▼
FastAPI AuthService
   │  2. Verify Argon2id hash & status
   │  3. Issue JWT Access Token (60m)
   │  4. Generate Opaque Refresh Token (7d)
   │  5. Save SHA-256 hash in user_sessions table
   ▼
Response
   ├── Set-Cookie: access_token=JWT; HttpOnly; SameSite=Lax; Secure
   ├── Set-Cookie: refresh_token=RAW; HttpOnly; SameSite=Lax; Secure
   └── Body: { access_token, refresh_token, token_type, expires_in, user }
```

---

## 4. Token Rotation & Replay Attack Protection

To prevent token theft and long-term session hijacking:

1. **Single-Use Rotation**: When `POST /api/v1/auth/refresh` is called, the provided refresh token is immediately marked `is_revoked = True`. A brand-new refresh token is issued and persisted in `user_sessions`.
2. **Replay Detection**: If an attacker attempts to reuse an already-rotated (revoked) refresh token:
   - The system recognizes that a previously spent token has resurfaced.
   - **Full Session Invalidation**: All active sessions belonging to that user ID are immediately revoked (`UPDATE user_sessions SET is_revoked = TRUE WHERE user_id = :uid`).
   - The request is aborted with HTTP 401 `AUTHENTICATION_REQUIRED` (`"Revoked refresh token detected. Session terminated for security."`).

---

## 5. Sliding-Window Rate Limiting

Authentication endpoints are protected against brute-force attacks via `SlidingWindowRateLimiter`:
- **Tracking Key**: `{client_ip}:{email}`
- **Threshold**: 5 failed login attempts within a rolling 900-second (15-minute) window.
- **Enforcement**:
  - Each invalid credential attempt appends a timestamp to the sliding window.
  - Exceeding 5 failures raises HTTP 429 `RATE_LIMIT_EXCEEDED`.
  - A successful authentication instantly purges failed attempt records for that key.

---

## 6. Authorization & Reusable Dependencies

| Dependency | Purpose | Failure Code |
| :--- | :--- | :--- |
| `get_current_user` | Resolves user identity from `Authorization: Bearer <token>` or `access_token` cookie. Eagerly joins `UserProfile`. | 401 Unauthorized |
| `require_active_user` | Enforces that user is not suspended or deactivated. | 403 Forbidden |
| `require_role(role)` | Factory enforcing required RBAC role (`candidate` or `admin`). Admins always pass. | 403 Forbidden |
| `ensure_resource_ownership(user, resource_id)` | Enforces that candidates can only view or mutate their own data. Admins bypass. | 403 Forbidden |

---

## 7. Audit & Activity Logging

All authentication state changes create structured records in `activity_logs`:
- `ACCOUNT_REGISTERED`: Logged when registration completes with client IP and initial status.
- `USER_LOGIN`: Logged upon successful authentication with client IP and session timestamp.
- `USER_LOGOUT`: Logged when candidate logs out, with session revocation.
