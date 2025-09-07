# Auth Service

A FastAPI-based authentication service that provides user registration, login, and account deletion functionality with secure password hashing.

## Features

- **User Registration**: Create new user accounts with email and password
- **User Login**: Authenticate existing users with email and password
- **Account Deletion**: Remove user accounts securely
- **Password Security**: Uses bcrypt hashing for password encryption
- **Database Integration**: SQLite database with proper DAO pattern implementation
- **REST API**: Clean RESTful API endpoints with proper HTTP status codes

## Tech Stack

- **Framework**: FastAPI
- **Database**: SQLite
- **Password Hashing**: SHA3-384
- **Data Validation**: Pydantic
- **Server**: Uvicorn
- **Python**: 3.12+

## API Endpoints

### Register User
- **POST** `/register`
- **Request Body**:
  ```json
  {
    "login": "user",
    "password": "securepassword123"
  }
  ```
- **Response**: `201 Created` with user ID
- **Description**: Creates a new user account with the provided email and password

### Login User
- **POST** `/login`
- **Request Body**:
  ```json
  {
    "login": "user",
    "password": "securepassword123"
  }
  ```
- **Response**: 
  - `201 Created` with success message for valid credentials
  - `404 Not Found` if user doesn't exist
  - `401 Unauthorized` if password is incorrect
- **Description**: Authenticates a user with email and password

### Delete Account
- **POST** `/delete`
- **Request Body**:
  ```json
  {
    "login": "user@example.com",
    "password": "securepassword123"
  }
  ```
- **Response**: 
  - `200 OK` with success message for valid credentials
  - `404 Not Found` if user doesn't exist
  - `401 Unauthorized` if password is incorrect
- **Description**: Deletes a user account after verifying credentials

## Project Structure

```
src/
├── app.py                 # FastAPI application entry point
├── routes/
│   └── api.py            # API route definitions
├── database/
│   ├── connection.py     # Database connection management
│   ├── schema.sql        # Database schema
│   └── dao/
│       └── users.py      # Data Access Object for users
├── crypto/
│   └── utils.py          # Password encryption utilities
└── dto/
    └── api.py            # Data Transfer Objects for API
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -e .
   ```
3. Set up the database (schema will be created automatically on first run)

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

- Passwords are hashed using SHA3-384 algorithm
- Database transactions are properly managed with context managers
- Input validation using Pydantic models
- Proper error handling and logging

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

## License

This project is licensed under the APGL-3.0 License - see the [LICENSE](LICENSE) file for details.