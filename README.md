# Chat App API

A scalable real-time chat application built with **FastAPI**, **MongoDB**, **Redis**, and **WebSockets**. The project follows a service-based architecture and is designed to support horizontal scaling using Redis Pub/Sub.

---

# Features

* JWT Authentication
* Google OAuth2 Sign In
* Email Verification (OTP)
* Redis-based Email Queue Worker
* One-to-One Conversations
* Real-Time Messaging with WebSockets
* MongoDB (Beanie ODM)
* Redis Caching and Pub/Sub
* Service Layer Architecture
* Dependency Injection
* Docker Friendly

---

# Tech Stack

| Technology | Purpose                 |
| ---------- | ----------------------- |
| FastAPI    | REST API                |
| MongoDB    | Database                |
| Beanie     | MongoDB ODM             |
| Redis      | Cache, Pub/Sub, Queue   |
| WebSocket  | Real-time communication |
| JWT        | Authentication          |
| SMTP       | Sending emails          |
| Docker     | Deployment              |

---

# Project Structure

```text
app/
│
├── api/                 # API routers
├── core/                # Application configuration
├── database/            # MongoDB and Redis connections
├── dependencies/        # FastAPI dependencies
├── middleware/          # Custom middleware
├── models/              # Database models
├── schemas/             # Request/Response schemas
├── services/            # Business logic
├── utils/               # Utility functions
├── websocket/           # WebSocket infrastructure
└── main.py
```

---

# Architecture

The project follows a layered architecture.

```
Client
   │
   ▼
Routers
   │
   ▼
Services
   │
   ├── MongoDB
   ├── Redis
   ├── Email Queue
   └── WebSocket Manager
```

Business logic is placed inside the `services` package while routers only handle HTTP requests and responses.

---

# Authentication

The application uses JWT authentication.

Access Token

* Sent inside the Authorization header.

Refresh Token

* Stored as an HttpOnly cookie.

Supported login methods:

* Email & Password
* Google OAuth2

---

# Email Verification

User registration requires email verification.

Flow:

```
Register
      │
      ▼
Generate OTP
      │
      ▼
Store OTP in Redis
      │
      ▼
Push email job to Redis Queue
      │
      ▼
Email Worker sends email
      │
      ▼
User verifies OTP
      │
      ▼
Account created
```

---

# Email Worker

The email worker is a completely separate process from the FastAPI application.

Its responsibility is to consume email jobs from Redis and send emails asynchronously.

Benefits:

* Fast API responses
* No waiting for SMTP
* Can run multiple workers
* Easy to scale independently

Example architecture:

```
          FastAPI
             │
             │ LPUSH
             ▼
      Redis Email Queue
             │
          BLPOP
             ▼
      Email Worker
             │
             ▼
        SMTP Server
             │
             ▼
         User Inbox
```

Run the worker separately:

```bash
python -m email_worker.main
```

The worker continuously waits for new email jobs using Redis `BLPOP` and processes them as they arrive.

---

# WebSocket System

The project supports real-time messaging using WebSockets.

Components:

* `manager.py`

  * Tracks connected users.

* `dispatcher.py`

  * Routes incoming events.

* `pub_sub.py`

  * Synchronizes messages between multiple API instances using Redis Pub/Sub.

This architecture allows multiple FastAPI servers to deliver messages correctly to connected users.

---

# Redis Usage

Redis is used for multiple purposes:

* OTP storage
* Temporary registration data
* Email queue
* WebSocket Pub/Sub
* JWT storage

---

# MongoDB Collections

## Users

Stores:

* Account information
* Authentication providers
* Profile information

---

## Conversations

Stores:

* Conversation members
* Last message
* Last activity

---

## Messages

Stores:

* Sender
* Conversation
* Content
* Timestamp

---

# API Modules

Current routers:

```
Auth
Registration
OAuth2
Users
Conversations
Messages
WebSocket
```


