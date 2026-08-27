# Task Management API

A production-oriented REST API for managing tasks with user authentication, JWT access/refresh tokens, ownership-based authorization, PostgreSQL, Docker, automated testing, and CI/CD.

## 🚀 Features

- User registration and authentication
- JWT-based authentication
- Access and refresh token support
- Refresh token revocation on logout
- Password hashing
- Task CRUD operations
- User-based task ownership
- Authorization to prevent users from accessing or modifying other users' tasks
- PostgreSQL database
- SQLAlchemy ORM
- Alembic database migrations
- Pydantic request/response validation
- Automated API tests with Pytest
- Docker and Docker Compose support
- GitHub Actions CI pipeline
- Interactive Swagger API documentation

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Language | Python |
| Framework | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Migrations | Alembic |
| Authentication | JWT |
| Validation | Pydantic |
| Testing | Pytest |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| API Documentation | Swagger UI / OpenAPI |
| Version Control | Git, GitHub |

## 📁 Project Structure

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
│   │   └── user.py
│   │
│   ├── services/
│   │   ├── user.py
│   │   └── task.py
│   │
│   ├── config.py
│   ├── database.py
│   ├── dependencies.py
│   └── security.py
│
├── alembic/
│   └── versions/
│
├── tests/
│   ├── conftest.py
│   └── test_tasks.py
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── main.py
├── requirements.txt
└── README.md
```

## 🔐 Authentication

The API uses JWT-based authentication.

### Authentication flow

```text
Client
  │
  ├── Register
  │      ↓
  │   User stored in PostgreSQL
  │
  ├── Login
  │      ↓
  │   Access Token + Refresh Token
  │
  ├── Access protected endpoints
  │      ↓
  │   JWT validation
  │
  ├── Refresh token
  │      ↓
  │   New access token
  │
  └── Logout
         ↓
     Refresh token revoked
```

Passwords are stored as password hashes rather than plain-text passwords.

## 📌 API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Authenticate user |
| POST | `/auth/refresh` | Generate a new access token |
| POST | `/auth/logout` | Revoke refresh token |
| GET | `/auth/me` | Get current authenticated user |

### Tasks

| Method | Endpoint | Description |
|---|---|---|
| POST | `/tasks/` | Create a task |
| GET | `/tasks/` | Get user's tasks |
| GET | `/tasks/{task_id}` | Get a specific task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

All protected task endpoints require authentication.

## 🛡️ Authorization

Tasks belong to the user who created them.

For example:

```text
User A
  │
  └── Task #10

User B
  │
  └── Cannot access Task #10
```

The API verifies the authenticated user's identity before allowing access, modification, or deletion of a task.

This prevents unauthorized users from manipulating another user's data.

## 🗄️ Database

The application uses PostgreSQL with SQLAlchemy as the ORM.

Main entities include:

```text
User
 ├── id
 ├── email
 ├── password_hash
 ├── is_active
 └── created_at
       │
       └── Tasks
```

Database schema changes are managed using Alembic migrations.

## 🐳 Running with Docker

Make sure Docker Desktop is installed and running.

Start the application:

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

Stop the containers:

```bash
docker compose down
```

To stop containers and remove the database volume:

```bash
docker compose down -v
```

> `docker compose down -v` removes the PostgreSQL Docker volume and therefore deletes the local database data.

## 💻 Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/Sahill858/task-management-api.git
cd task-management-api
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv venv
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

Create a `.env` file:

```env
APP_NAME=Task Management API
APP_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/task_management
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Never commit `.env` or real secrets to GitHub.

### 5. Run the API

```bash
uvicorn main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

## 🧪 Testing

The project uses Pytest for automated testing.

Run:

```bash
pytest
```

Current test suite:

```text
13 passed
```

The tests cover authentication, task operations, refresh/logout behavior, and authorization between different users.

## 🔄 CI/CD

GitHub Actions automatically runs the test suite when changes are pushed to the repository or a pull request targets the `main` branch.

CI pipeline:

```text
Git Push / Pull Request
        ↓
GitHub Actions
        ↓
Set up Python
        ↓
Install dependencies
        ↓
Start PostgreSQL service
        ↓
Run Pytest
        ↓
Pass / Fail
```

A successful pipeline ensures that the automated tests pass before changes are considered ready.

## ⚙️ Environment Variables

| Variable | Description |
|---|---|
| `APP_NAME` | Application name |
| `APP_ENV` | Application environment |
| `SECRET_KEY` | Secret used for JWT signing |
| `DATABASE_URL` | PostgreSQL connection URL |
| `JWT_ALGORITHM` | JWT signing algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime |

## 📖 API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

```text
http://localhost:8000/docs
```

ReDoc:

```text
http://localhost:8000/redoc
```

Swagger can be used to register users, authenticate, obtain tokens, and test protected task endpoints directly from the browser.

## 🎯 What I Learned

This project helped me practice real-world backend development concepts including:

- REST API design
- FastAPI application structure
- Authentication and authorization
- JWT access and refresh tokens
- Password hashing
- SQLAlchemy ORM
- PostgreSQL database design
- Database migrations with Alembic
- Dependency injection
- Automated API testing
- Docker containerization
- Docker Compose
- Git and GitHub workflows
- Continuous Integration with GitHub Actions

## 🔮 Future Improvements

Possible future improvements include:

- Role-based access control
- Task filtering and pagination
- Redis caching
- Background task processing
- Production deployment
- API rate limiting
- Improved logging and monitoring

## 👨‍💻 Author

**Sahil Kumar Sahu**

Python Backend Developer

GitHub: `https://github.com/Sahill858`

---

⭐ If you find this project useful, feel free to explore the repository and API documentation.