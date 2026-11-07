# Supabase Auth: Login & Protect

FlyRank Internship Backend Track · Week 2 · Assignment A4

A secure RESTful authentication service built with **FastAPI** and backed by **Supabase Auth** as the external Identity Provider (IdP). Features user registration, credential authentication, JWT token issuance, Bearer token verification middleware, and interactive Swagger UI bearer authorization.

---

## 1. What This Is

* **No Homemade Crypto**: Passwords and cryptographic token signatures are managed entirely by Supabase Auth — the backend never stores raw passwords or implements custom hashing algorithms.
* **Stateless JWT Security**: The server verifies access tokens (JWTs) using Supabase's cryptographic verification (`supabase.auth.get_user(token)`), turning away forged or expired passes with `401 Unauthorized`.
* **Reusable Guard Dependency**: Protected endpoints share a single dependency (`get_current_user`) that extracts and validates the `Authorization: Bearer <token>` header before invoking the route handler.

---

## 2. Quickstart & Installation

### Install Dependencies
```bash
pip install fastapi uvicorn supabase python-dotenv
```

### Environment Configuration
Copy the template and provide your Supabase project credentials:
```bash
cp .env.example .env
```

Inside `.env`:
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
PORT=8000
```
> **Security Note:** `.env` is listed in `.gitignore` and is never committed to GitHub.

---

## 3. One Command to Run

```bash
uvicorn main:app --reload
```
The server will start locally at **`http://localhost:8000`**.  
Interactive documentation (Swagger UI): **`http://localhost:8000/docs`**

---

## 4. API Endpoints Reference

| Method | Endpoint | Description | Auth Required? | Expected Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | API Health & Discovery | None | `200 OK` |
| `GET` | `/public/info` | Open public information | None | `200 OK` |
| `POST` | `/auth/signup` | Register a new user | None | `201 Created`, `400 Bad Request` |
| `POST` | `/auth/login` | Authenticate & retrieve JWT tokens | None | `200 OK`, `400 Bad Request`, `401 Unauthorized` |
| `GET` | `/protected/profile` | Read authenticated user profile | Bearer Token | `200 OK`, `401 Unauthorized` |
| `GET` | `/protected/dashboard`| Second protected resource | Bearer Token | `200 OK`, `401 Unauthorized` |
| `POST` | `/auth/logout` | Terminate session | Bearer Token | `204 No Content`, `401 Unauthorized` |

---

## 5. Sample `curl -i` Verification Commands

### 1. Register a New User (`POST /auth/signup`)
```powershell
curl.exe --% -i -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" -d "{\"email\":\"developer@example.com\",\"password\":\"SecurePassword123!\"}"
```
```http
HTTP/1.1 201 Created
content-type: application/json

{"id":"5495500e-eb87-42db-a54a-3814fe646c2f","email":"developer@example.com","created_at":"2026-11-07 20:29:33"}
```

### 2. Log In & Receive Access Token (`POST /auth/login`)
```powershell
curl.exe --% -i -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" -d "{\"email\":\"developer@example.com\",\"password\":\"SecurePassword123!\"}"
```
```http
HTTP/1.1 200 OK
content-type: application/json

{"access_token":"eyJhbGciOiJFUzI1Ni...","refresh_token":"...","token_type":"bearer","expires_in":3600}
```

### 3. Access Protected Route (`GET /protected/profile`)
```powershell
curl.exe -i http://localhost:8000/protected/profile -H "Authorization: Bearer <PASTE_YOUR_ACCESS_TOKEN>"
```
```http
HTTP/1.1 200 OK
content-type: application/json

{"id":"5495500e-eb87-42db-a54a-3814fe646c2f","email":"developer@example.com","created_at":"2026-11-07 20:29:33"}
```

### 4. Forged / Tampered Token Rejection
```powershell
curl.exe -i http://localhost:8000/protected/profile -H "Authorization: Bearer forged_invalid_token"
```
```http
HTTP/1.1 401 Unauthorized
content-type: application/json

{"error":"Invalid or expired token"}
```

### 5. Missing Token Rejection
```powershell
curl.exe -i http://localhost:8000/protected/profile
```
```http
HTTP/1.1 401 Unauthorized
content-type: application/json

{"error":"Access token required"}
```

---

## 6. Interactive Swagger UI with Authorize Padlock

FastAPI provides built-in Swagger documentation at:  
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

1. Open `/docs` in your browser.
2. Click the green **Authorize** padlock button at the top right.
3. Paste the `access_token` from `/auth/login` into the `Value` field and click **Authorize**.
4. Test any protected route (`/protected/profile`, `/protected/dashboard`, `/auth/logout`) directly using **Try it out**!

![Swagger UI Authorize Padlock Screenshot](swagger_auth.png)

---

## 7. Clean Clone Verification

A reviewer can clone and run this project in under 3 minutes:

```bash
cd 04-auth-login-protect
cp .env.example .env
# Edit .env with your Supabase credentials
pip install -r requirements.txt
uvicorn main:app --reload
```
