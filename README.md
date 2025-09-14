# Auth Service

A FastAPI-based authentication service that provides user registration, login, account deletion, and JWT token management with secure password hashing using bcrypt.

## Features

- **User Registration**: Create new user accounts with login and password
- **User Login**: Authenticate existing users and receive JWT tokens
- **Account Deletion**: Remove user accounts securely
- **JWT Authentication**: Secure token-based authentication with Redis session management
- **Password Security**: Uses bcrypt hashing for password encryption
- **Database Integration**: PostgreSQL database with proper DAO pattern implementation
- **Redis Session Management**: Token storage and validation
- **REST API**: Clean RESTful API endpoints with proper HTTP status codes
- **User Profile**: Retrieve current user profile information
- **Logout**: Secure token revocation

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Cache/Session**: Redis
- **Password Hashing**: bcrypt
- **Authentication**: JWT (JSON Web Tokens)
- **Data Validation**: Pydantic
- **Server**: Uvicorn
- **Python**: 3.12+

## API Endpoints

### Register User
- **POST** `/api/register`
- **Request Body**:
  ```json
  {
    "login": "user",
    "password": "securepassword123"
  }
  ```
- **Response**: `201 Created` with user ID
- **Description**: Creates a new user account with the provided login and password

### Login User
- **POST** `/api/login`
- **Request Body**:
  ```json
  {
    "login": "user",
    "password": "securepassword123"
  }
  ```
- **Response**:
  - `200 OK` with JWT token for valid credentials
  - `401 Unauthorized` if credentials are invalid
- **Description**: Authenticates a user and returns a JWT access token

### Logout User
- **POST** `/api/logout`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` with success message
- **Description**: Logs out the user by revoking their token

### Get User Profile
- **GET** `/api/profile`
- **Headers**: `Authorization: Bearer <token>`
- **Response**: `200 OK` with user profile data
- **Description**: Retrieves the current authenticated user's profile

### Delete Account
- **POST** `/api/delete`
- **Request Body**:
  ```json
  {
    "login": "user",
    "password": "securepassword123"
  }
  ```
- **Headers**: `Authorization: Bearer <token>` (optional for security)
- **Response**:
  - `200 OK` with success message for valid credentials
  - `401 Unauthorized` if credentials are invalid
- **Description**: Deletes a user account after verifying credentials

### Health Check
- **GET** `/health`
- **Response**: `200 OK` with service status
- **Description**: Health check endpoint for monitoring

## Project Structure

```
src/
├── app.py                 # FastAPI application entry point
├── routes/
│   ├── api.py            # Main API routes (auth, profile, etc.)
│   └── health.py         # Health check endpoint
├── database/
│   ├── connection.py     # Database connection management
│   ├── settings.py       # Database and application settings
│   ├── schema.sql        # Database schema
│   ├── dao/
│   │   ├── users.py      # Data Access Object for users
│   │   └── tokens.py     # Data Access Object for tokens
│   └── redis_connection.py # Redis connection management
├── crypto/
│   └── utils.py          # Password encryption utilities (bcrypt)
└── dto/
    └── api.py            # Data Transfer Objects for API
```

## Installation

### Prerequisites
- Python 3.12+
- PostgreSQL database
- Redis server

### Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Set up environment variables (create a `.env` file):
   ```bash
   # Database
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=auth_db
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   
   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0
   
   # JWT
   SECRET_KEY=your-secret-key-here
   ```
4. Set up the database:
   - Create the PostgreSQL database
   - Run the schema from `src/database/schema.sql`

### Docker Development

1. Copy and configure environment variables:
   ```bash
   cp .example.dbenv .env
   # Edit .env with your configuration
   ```
2. Start the services:
   ```bash
   docker-compose up -d
   ```

The API will be available at `http://localhost:8000`

## Running the Application

```bash
uvicorn src.app:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, you can access:
- Interactive API documentation at `http://localhost:8000/docs`
- Alternative API documentation at `http://localhost:8000/redoc`

## Security Features

- **Password Security**: Passwords are hashed using bcrypt with salt
- **JWT Authentication**: Stateless authentication with configurable expiration
- **Session Management**: Token validation and storage in Redis
- **Input Validation**: Request/response validation using Pydantic models
- **Secure Token Handling**: Automatic token validation and refresh
- **Database Security**: Proper connection management and transaction handling
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes

## Development

### Running Tests

```bash
pytest
```

### Code Quality

The project uses various tools for code quality:
- **Ruff**: For linting and formatting
- **Bandit**: For security linting
- **Coverage**: For test coverage analysis
- **Pydantic**: For data validation and serialization

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | PostgreSQL database name | `auth_db` |
| `DB_USER` | PostgreSQL username | - |
| `DB_PASSWORD` | PostgreSQL password | - |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database number | `0` |
| `SECRET_KEY` | JWT secret key | - |

## License

This project is licensed under the APGL-3.0 License - see the [LICENSE](LICENSE) file for details.