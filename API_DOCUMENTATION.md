# REST API Documentation

## Base URL
```
http://localhost:5000/api/v1
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. After logging in or registering, you'll receive:
- **access_token**: Valid for 1 hour, used for API requests
- **refresh_token**: Valid for 7 days, used to get new access tokens

Include the access token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Endpoints

### Health Check

#### GET /health
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "api": "v1"
}
```

---

### Authentication

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe"
}
```

**Response:** (201 Created)
```json
{
  "message": "User registered successfully",
  "user": {
    "email_address": "user@example.com",
    "name": "John Doe"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### POST /auth/login
Login an existing user.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:** (200 OK)
```json
{
  "message": "Login successful",
  "user": {
    "email_address": "user@example.com",
    "name": "John Doe"
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### POST /auth/refresh
Refresh an expired access token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** (200 OK)
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### Emails

#### POST /emails
Send an email. **Requires authentication.**

**Request Body:**
```json
{
  "recipient": "recipient@example.com",
  "subject": "Meeting Tomorrow",
  "body": "Let's meet at 10 AM in the conference room."
}
```

**Response:** (201 Created)
```json
{
  "message": "Email sent successfully",
  "email": {
    "email_id": "550e8400-e29b-41d4-a716-446655440000",
    "sender": "user@example.com",
    "recipient": "recipient@example.com",
    "subject": "Meeting Tomorrow",
    "body": "Let's meet at 10 AM in the conference room.",
    "timestamp": "2025-12-22T18:00:00.000000",
    "read": false
  }
}
```

#### GET /emails/inbox
Get all emails in your inbox. **Requires authentication.**

**Response:** (200 OK)
```json
{
  "emails": [
    {
      "email_id": "550e8400-e29b-41d4-a716-446655440000",
      "sender": "sender@example.com",
      "recipient": "user@example.com",
      "subject": "Hello",
      "body": "Hi there!",
      "timestamp": "2025-12-22T18:00:00.000000",
      "read": false
    }
  ],
  "count": 1
}
```

#### GET /emails/sent
Get all emails you've sent. **Requires authentication.**

**Response:** (200 OK)
```json
{
  "emails": [
    {
      "email_id": "550e8400-e29b-41d4-a716-446655440000",
      "sender": "user@example.com",
      "recipient": "recipient@example.com",
      "subject": "Meeting Tomorrow",
      "body": "Let's meet at 10 AM.",
      "timestamp": "2025-12-22T18:00:00.000000",
      "read": false
    }
  ],
  "count": 1
}
```

#### GET /emails/<email_id>
Get a specific email by ID. **Requires authentication.**

**Response:** (200 OK)
```json
{
  "email": {
    "email_id": "550e8400-e29b-41d4-a716-446655440000",
    "sender": "sender@example.com",
    "recipient": "user@example.com",
    "subject": "Hello",
    "body": "Hi there!",
    "timestamp": "2025-12-22T18:00:00.000000",
    "read": false
  }
}
```

#### PUT /emails/<email_id>/read
Mark an email as read. **Requires authentication.**

**Response:** (200 OK)
```json
{
  "message": "Email marked as read",
  "email": {
    "email_id": "550e8400-e29b-41d4-a716-446655440000",
    "sender": "sender@example.com",
    "recipient": "user@example.com",
    "subject": "Hello",
    "body": "Hi there!",
    "timestamp": "2025-12-22T18:00:00.000000",
    "read": true
  }
}
```

---

### Users

#### GET /users
Get all registered users. **Requires authentication.**

**Response:** (200 OK)
```json
{
  "users": [
    {
      "email_address": "user1@example.com",
      "name": "User One"
    },
    {
      "email_address": "user2@example.com",
      "name": "User Two"
    }
  ],
  "count": 2
}
```

#### GET /users/me
Get current user information. **Requires authentication.**

**Response:** (200 OK)
```json
{
  "user": {
    "email_address": "user@example.com",
    "name": "John Doe"
  }
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

### Common HTTP Status Codes

- **200 OK**: Request succeeded
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication token
- **403 Forbidden**: User not authorized for this action
- **404 Not Found**: Resource not found

---

## Example Usage

### Python Example

```python
import requests

BASE_URL = "http://localhost:5000/api/v1"

# Register a user
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "alice@example.com",
    "name": "Alice"
})
data = response.json()
access_token = data['access_token']

# Send an email
headers = {"Authorization": f"Bearer {access_token}"}
response = requests.post(f"{BASE_URL}/emails", json={
    "recipient": "bob@example.com",
    "subject": "Hello",
    "body": "Hi Bob!"
}, headers=headers)

# Get inbox
response = requests.get(f"{BASE_URL}/emails/inbox", headers=headers)
inbox = response.json()
print(f"You have {inbox['count']} emails")
```

### cURL Examples

```bash
# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "name": "Alice"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com"}'

# Send email (replace TOKEN with your access_token)
curl -X POST http://localhost:5000/api/v1/emails \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"recipient": "bob@example.com", "subject": "Hello", "body": "Hi!"}'

# Get inbox
curl -X GET http://localhost:5000/api/v1/emails/inbox \
  -H "Authorization: Bearer TOKEN"
```

### Swift/iOS Example

```swift
import Foundation

struct APIClient {
    let baseURL = "http://localhost:5000/api/v1"
    var accessToken: String?
    
    func register(email: String, name: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/auth/register")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let body = ["email": email, "name": name]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            
            guard let data = data else {
                completion(.failure(NSError(domain: "", code: -1)))
                return
            }
            
            do {
                let authResponse = try JSONDecoder().decode(AuthResponse.self, from: data)
                completion(.success(authResponse))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }
    
    func getInbox(completion: @escaping (Result<InboxResponse, Error>) -> Void) {
        guard let token = accessToken else { return }
        
        let url = URL(string: "\(baseURL)/emails/inbox")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        
        URLSession.shared.dataTask(with: request) { data, response, error in
            // Handle response...
        }.resume()
    }
}

struct AuthResponse: Codable {
    let accessToken: String
    let refreshToken: String
    let user: User
    
    enum CodingKeys: String, CodingKey {
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
        case user
    }
}

struct User: Codable {
    let emailAddress: String
    let name: String
    
    enum CodingKeys: String, CodingKey {
        case emailAddress = "email_address"
        case name
    }
}

struct InboxResponse: Codable {
    let emails: [Email]
    let count: Int
}

struct Email: Codable {
    let emailId: String
    let sender: String
    let recipient: String
    let subject: String
    let body: String
    let timestamp: String
    let read: Bool
    
    enum CodingKeys: String, CodingKey {
        case emailId = "email_id"
        case sender, recipient, subject, body, timestamp, read
    }
}
```

---

## Rate Limiting

Currently, there is no rate limiting implemented. For production use, consider adding rate limiting middleware.

## Security Notes

1. **JWT Secret**: Change the `JWT_SECRET` environment variable in production
2. **HTTPS**: Always use HTTPS in production
3. **Token Storage**: Store tokens securely on client devices (Keychain for iOS, KeyStore for Android)
4. **Token Expiration**: Access tokens expire after 1 hour, refresh tokens after 7 days
5. **CORS**: CORS is enabled for all origins (`*`). Restrict this in production.
