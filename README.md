# Task Management API

A production-style RESTful Task Management API built with **FastAPI, PostgreSQL, SQLAlchemy, JWT authentication, Alembic, Docker, and GitHub Actions CI/CD**.

The API supports user registration, authentication, refresh-token management, and secure CRUD operations for user-owned tasks.

## Live Demo

**Swagger API Documentation:**  
https://task-management-api-rplu.onrender.com/docs

**API Health Check:**  
https://task-management-api-rplu.onrender.com/

## Features

### Authentication

- User registration
- Secure password hashing
- JWT access-token authentication
- Refresh-token authentication
- Refresh-token expiration
- Refresh-token revocation on logout
- Current-user endpoint
- Active/inactive user validation

### Task Management

- Create tasks
- Get authenticated user's tasks
- Get a specific task
- Update tasks
- Delete tasks
- Pagination using `skip` and `limit`
- Filter tasks by status
- Filter tasks by priority
- Sort tasks by selected fields
- Ascending/descending ordering

### Security

- Passwords are never stored in plain text
- JWT-based authentication
- User-specific task authorization
- Users cannot access, modify, or delete another user's tasks
- Refresh tokens are stored and tracked in PostgreSQL
- Environment variables are used for application secrets

### Database & Migrations

- PostgreSQL database
- SQLAlchemy 2.0 ORM
- Alembic database migrations
- User-to-task relationship
- User-to-refresh-token relationship
- Foreign-key constraints and indexes

### DevOps

- Docker support
- GitHub Actions CI
- Automated pytest execution
- Supabase PostgreSQL
- Render deployment

---

## Tech Stack

| Category          | Technology        |
| ----------------- | ----------------- |
| Language          | Python 3.13       |
| Framework         | FastAPI           |
| ORM               | SQLAlchemy 2.0    |
| Database          | PostgreSQL        |
| Database Hosting  | Supabase          |
| Migrations        | Alembic           |
| Authentication    | JWT               |
| Password Hashing  | Argon2 / pwdlib   |
| Validation        | Pydantic          |
| Testing           | Pytest            |
| Containerization  | Docker            |
| CI/CD             | GitHub Actions    |
| Deployment        | Render            |
| API Documentation | Swagger / OpenAPI |
| Version Control   | Git / GitHub      |

---

## Project Structure

```text
task-management-api/
│
├── app/
│   ├── models/
│   │   ├── user.py
│   │   ├── task.py
│   │   └── refresh_token.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   └── task.py
│   │
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── task.py
│   │
│   ├── services/
│   │   ├── user.py
│   │   └── task.py
│   │
│   ├── workers/
│   │
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   └── security.py
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── tests/
│   └── test_tasks.py
│
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
└── README.md
```

---

## API Endpoints

### Authentication

| Method | Endpoint         | Description                 | Authentication |
| ------ | ---------------- | --------------------------- | -------------- |
| POST   | `/auth/register` | Register a new user         | No             |
| POST   | `/auth/login`    | Login and receive tokens    | No             |
| GET    | `/auth/me`       | Get current user            | JWT            |
| POST   | `/auth/refresh`  | Generate a new access token | Refresh token  |
| POST   | `/auth/logout`   | Revoke refresh token        | Refresh token  |

### Tasks

| Method | Endpoint           | Description      | Authentication |
| ------ | ------------------ | ---------------- | -------------- |
| POST   | `/tasks/`          | Create a task    | JWT            |
| GET    | `/tasks/`          | Get user's tasks | JWT            |
| GET    | `/tasks/{task_id}` | Get a task       | JWT            |
| PATCH  | `/tasks/{task_id}` | Update a task    | JWT            |
| DELETE | `/tasks/{task_id}` | Delete a task    | JWT            |

### System

| Method | Endpoint     | Description                 |
| ------ | ------------ | --------------------------- |
| GET    | `/`          | API status                  |
| GET    | `/health/db` | Database connectivity check |

---

## Task Listing

The task listing endpoint supports pagination, filtering, and sorting.

Example:

```text
GET /tasks/?skip=0&limit=10
```

Filter by status:

```text
GET /tasks/?status=pending
```

Filter by priority:

```text
GET /tasks/?priority=high
```

Sort tasks:

```text
GET /tasks/?sort_by=created_at&order=desc
```

These parameters can also be combined.

---

## Authentication Flow

The authentication system uses short-lived access tokens and persistent refresh tokens.

```text
                ┌──────────────┐
                │    Register  │
                └──────┬───────┘
                       │
                       ▼
                ┌──────────────┐
                │     Login    │
                └──────┬───────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
       Access Token       Refresh Token
              │                 │
              ▼                 ▼
        API Requests       PostgreSQL
              │                 │
              │          ┌──────┴──────┐
              │          │   Refresh   │
              │          └──────┬──────┘
              │                 │
              │                 ▼
              │          New Access Token
              │
              ▼
        Protected API
```

### Access Token

The access token is used when accessing protected endpoints:

```text
Authorization: Bearer <access_token>
```

### Refresh Token

When the access token needs to be renewed, the refresh token is sent to:

```text
POST /auth/refresh
```

The server validates:

- Token signature
- Stored token
- Revocation status
- Expiration
- User ID

A new access token is then generated.

### Logout

When a user logs out, the stored refresh token is marked as revoked.

This prevents the revoked refresh token from being used again.

---

## Authorization

Tasks belong to the user who created them.

The relationship is:

```text
User
 │
 ├── Task
 ├── Task
 └── Task
```

When accessing a task, the API verifies:

```text
task.user_id == current_user.id
```

If the task belongs to another user, the API returns:

```text
404 Task not found
```

This prevents users from accessing another user's task data.

The same authorization check is applied to:

- GET
- PATCH
- DELETE

---

## Database Design

The application currently uses three main tables.

### Users

Stores registered users.

```text
users
├── id
├── email
├── password_hash
├── is_active
└── created_at
```

### Tasks

Stores tasks belonging to users.

```text
tasks
├── id
├── user_id → users.id
├── title
├── description
├── status
├── priority
└── created_at
```

### Refresh Tokens

Stores refresh tokens associated with users.

```text
refresh_tokens
├── id
├── token
├── user_id → users.id
├── expires_at
├── is_revoked
└── created_at
```

Relationships:

```text
users
  │
  ├──────────────< tasks
  │
  └──────────────< refresh_tokens
```

---

## Local Development

### 1. Clone the repository

```bash
git clone https://github.com/Sahill858/task-management-api.git
cd task-management-api
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
APP_NAME=Task Management API
APP_ENV=development

SECRET_KEY=your-secret-key

DATABASE_URL=your-postgresql-database-url

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Never commit the `.env` file to Git.

---

## Database Migrations

The project uses Alembic to manage database schema changes.

Apply all migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "Describe the change"
```

Then review the generated migration before applying it:

```bash
alembic upgrade head
```

---

## Run the Application

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

## Running Tests

Run the complete test suite:

```bash
pytest
```

Current test status:

```text
13 passed
```

The test suite covers authentication, task operations, token handling, and user-level task authorization.

---

## CI with GitHub Actions

The project uses GitHub Actions to automatically run tests when changes are pushed to the `main` branch or when a pull request targets `main`.

The CI workflow:

```text
Git Push / Pull Request
        │
        ▼
Checkout Repository
        │
        ▼
Setup Python 3.13
        │
        ▼
Install Dependencies
        │
        ▼
Start PostgreSQL Service
        │
        ▼
Run Pytest
        │
        ▼
   Tests Passed
```

This helps prevent broken code from being merged into the main branch.

---

## Deployment

The application is deployed using:

```text
GitHub
   │
   ▼
Render
   │
   ▼
FastAPI Application
   │
   ▼
Supabase PostgreSQL
```

### Production Components

**Application hosting:** Render

**Database hosting:** Supabase PostgreSQL

**Source control:** GitHub

**CI:** GitHub Actions

### Production Start Command

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Health Checks

Application health:

```text
GET /
```

Database health:

```text
GET /health/db
```

A successful database health response:

```json
{
  "database": "connected"
}
```

---

## Example API Workflow

### 1. Register

```http
POST /auth/register
```

```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### 2. Login

```http
POST /auth/login
```

The API returns an access token and refresh token.

### 3. Create a task

Send the access token:

```text
Authorization: Bearer <access_token>
```

Then:

```http
POST /tasks/
```

Example body:

```json
{
  "title": "Complete backend project",
  "description": "Finish API deployment",
  "status": "pending",
  "priority": "high"
}
```

### 4. Retrieve tasks

```http
GET /tasks/
```

Only tasks belonging to the authenticated user are returned.

---

## Security Considerations

The project follows several common backend security practices:

- Password hashing instead of storing plain-text passwords
- JWT authentication for protected endpoints
- Refresh-token persistence and revocation
- Environment-based configuration
- Database foreign-key relationships
- User-level authorization
- Generic invalid-login error responses
- Production secrets kept outside source control

---

## Future Improvements

Potential improvements for future versions:

- Role-based access control
- Email verification
- Password reset functionality
- Task due dates
- Task categories/tags
- Soft deletion
- Rate limiting
- Redis caching
- Background jobs
- Structured application logging
- Centralized exception handling
- API versioning
- Docker-based production deployment
- Monitoring and observability
- Expanded integration and security testing

---

## Author

**Sahil Kumar Sahu**

Python Backend Developer

- GitHub: https://github.com/Sahill858
- LinkedIn: https://linkedin.com/in/sahilsahuofficial

---

## License

This project is intended for learning, portfolio demonstration, and backend development practice.
