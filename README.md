# Auth Service

A FastAPI-based authentication service that provides user registration, login, account deletion, and JWT token management with secure password hashing using bcrypt. The service runs behind a Premier gateway with SSL termination, rate limiting, and monitoring capabilities.

**Version**: 0.1.0
**Python**: 3.12+
**Package Manager**: UV

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
- **Gateway**: Premier (ASGI Gateway with rate limiting, monitoring)
- **Database**: PostgreSQL
- **Cache/Session**: Redis
- **Password Hashing**: bcrypt
- **Authentication**: JWT (JSON Web Tokens)
- **Data Validation**: Pydantic
- **Server**: Uvicorn
- **Python**: 3.12+
- **SSL/TLS**: HTTPS with certificate termination

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
2. Install dependencies using UV (recommended):
   ```bash
   uv sync
   ```
   Or using pip:
   ```bash
   pip install -e .
   ```
3. Set up environment variables (create a `.env` file):
   ```bash
   # Database
   DB_HOST=localhost
   DB_PORT=5432
   DB_USER=auth_user
   DB_PASSWORD=password
   DB_TABLE=auth

   # Redis
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_DB=0

   # JWT
   SECRET_KEY=your-secret-key-here

   # SSL (for local development with HTTPS)
   SSL_CERTFILE=.ssl/cert.pem
   SSL_KEYFILE=.ssl/key.pem
   ```
4. Set up the database:
   - Create the PostgreSQL database
   - Run the schema from `src/database/schema.sql`
5. Generate SSL certificates (for HTTPS):
   ```bash
   mkdir -p .ssl
   openssl req -x509 -newkey rsa:4096 -keyout .ssl/key.pem -out .ssl/cert.pem -days 365 -nodes
   ```

### Docker Development

1. Copy and configure environment variables:
   ```bash
   cp .db.env.example .db.env
   # Edit .db.env with your configuration
   ```
2. Set up SSL certificates:
   ```bash
   mkdir -p .ssl
   # Place your SSL certificate files at:
   # - .ssl/cert.pem
   # - .ssl/key.pem
   ```
3. Start the services:
   ```bash
   docker-compose up -d
   ```

The API will be available at `https://localhost:443` (HTTPS)

## Running the Application

### Local Development

```bash
# Using UV (recommended)
uv run gateway.py

# Or using uvicorn directly
uvicorn gateway:gateway --host 0.0.0.0 --port 443 --ssl-certfile .ssl/cert.pem --ssl-keyfile .ssl/key.pem --workers 4
```

The API will be available at `https://localhost:443` (HTTPS)

### Premier Gateway Setup

The application uses a Premier gateway configuration defined in [`gateway.py`](gateway.py:1) and [`premier.yml`](premier.yml:1). The gateway provides:

- **ASGI Gateway**: Integration with FastAPI through Premier
- **Redis Caching**: AsyncRedisCache for token management
- **Configuration**: GatewayConfig loaded from premier.yml file
- **Load Balancing**: Built-in support for multiple instances

To run with the Premier gateway:
```bash
uv run gateway.py
```

### Production

```bash
uvicorn gateway:gateway --host 0.0.0.0 --port 443 --ssl-certfile .ssl/cert.pem --ssl-keyfile .ssl/key.pem --workers 4
```

## API Documentation

Once running, you can access:
- Interactive API documentation at `https://localhost:443/docs`
- Alternative API documentation at `https://localhost:443/redoc`

## Premier Gateway Configuration

The service is configured with a Premier gateway that provides:

- **Rate Limiting**: 100 requests per minute per endpoint
- **Monitoring**: Request logging with 5.0 second threshold
- **SSL Termination**: HTTPS support with certificate management
- **ASGI Compatibility**: Full async support with FastAPI

Configuration is managed through `premier.yml`:

```yaml
premier:
  paths:
    - pattern: "/api/*"
      features:
        rate_limit:
          quota: 100
          duration: 60
        monitoring:
          log_threshold: 5.0
```

## Security Features

- **Password Security**: Passwords are hashed using bcrypt with salt
- **JWT Authentication**: Stateless authentication with configurable expiration
- **Session Management**: Token validation and storage in Redis
- **Input Validation**: Request/response validation using Pydantic models
- **Secure Token Handling**: Automatic token validation and refresh
- **Database Security**: Proper connection management and transaction handling
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes
- **SSL/TLS**: HTTPS encryption with proper certificate handling
- **Rate Limiting**: Protection against brute force attacks

## Development

### Package Management

This project uses **UV**, a modern Python package manager for fast and reliable dependency management:

```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --dev

# Run the application
uv run gateway.py

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=src --cov-report=html
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest test/test_app.py

# Run tests with verbose output
pytest -v
```

### Code Quality

The project uses various tools for code quality:
- **Ruff**: For linting and formatting
- **Bandit**: For security linting
- **Coverage**: For test coverage analysis
- **Pydantic**: For data validation and serialization

### Pre-commit Hooks

The project includes pre-commit hooks for code quality:
```bash
pre-commit install
pre-commit run --all-files
```

### Development Tools

- **UV**: Modern Python package manager
- **Bandit**: Security linting
- **Ruff**: Fast Python linter and formatter
- **HTTPX**: For testing HTTP endpoints
- **Pytest**: Test framework with coverage support

### Dependencies

**Core Dependencies:**
- FastAPI >= 0.116.1
- PyJWT >= 2.9.0
- bcrypt >= 4.2.1
- psycopg-binary >= 3.2.10
- redis >= 6.4.0
- premier >= 0.4.10

**Development Dependencies:**
- pytest >= 8.0.0
- ruff >= 0.12.11
- bandit >= 1.8.6
- httpx >= 0.28.1
- pre-commit >= 3.8.0

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_USER` | PostgreSQL username | `auth_user` |
| `DB_PASSWORD` | PostgreSQL password | `password` |
| `DB_TABLE` | PostgreSQL database name | `auth` |
| `REDIS_HOST` | Redis host | `localhost` |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database number | `0` |
| `SECRET_KEY` | JWT secret key | - |
| `SSL_CERTFILE` | SSL certificate file path | `.ssl/cert.pem` |
| `SSL_KEYFILE` | SSL private key file path | `.ssl/key.pem` |
| `LOG_LEVEL` | Application logging level | `INFO` |

### Production Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DB_HOST` | PostgreSQL host | Yes |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_USER` | PostgreSQL username | Yes |
| `DB_PASSWORD` | PostgreSQL password | Yes |
| `DB_TABLE` | PostgreSQL database name | `auth` |
| `REDIS_HOST` | Redis host | Yes |
| `REDIS_PORT` | Redis port | `6379` |
| `REDIS_DB` | Redis database number | `0` |
| `SECRET_KEY` | JWT secret key (min 32 chars) | Yes |
| `LOG_LEVEL` | Application logging level | `INFO` |
| `SSL_CERTFILE` | SSL certificate file path | `/app/.ssl/cert.pem` |
| `SSL_KEYFILE` | SSL private key file path | `/app/.ssl/key.pem` |

## Production Deployment

### Docker Compose

For production deployment, use the provided [`compose.prod.yml`](compose.prod.yml:1) with advanced features:

```bash
# Copy and configure environment variables
cp .prod.env.example .prod.env
# Edit .prod.env with production configuration

# Set up SSL certificates
mkdir -p ssl
# Place your SSL certificate files at:
# - ssl/cert.pem
# - ssl/key.pem
# Set proper permissions: chmod 600 ssl/cert.pem ssl/key.pem

# Start services
docker-compose -f compose.prod.yml up -d

# View logs
docker-compose -f compose.prod.yml logs -f auth_api
```

### Production Features

The production configuration includes:

- **Resource Limits**: CPU and memory limits for each service
- **Health Checks**: Automated health monitoring for all services
- **Scaling**: Multiple replicas with rolling updates
- **Network**: Dedicated bridge network for service isolation
- **SSL Certificate Mounting**: Read-only SSL certificate volumes
- **Restart Policies**: Automatic restart on failure
- **Database Persistence**: Named volumes for data persistence

### SSL Certificate Setup

For production, use proper SSL certificates:

```bash
# Using Let's Encrypt (recommended for production)
sudo certbot certonly --standalone -d your-domain.com

# Copy certificates to the project
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem

# Set proper permissions
chmod 600 ssl/cert.pem ssl/key.pem
```

### Health Monitoring

The service includes health check endpoints:
- **Health Check**: `GET /health` - Returns service status (internal port 8000)
- **Docker Health Check**: Built into the Docker image with 30-second intervals
- **Service Dependencies**: Waits for PostgreSQL and Redis health checks before starting

### Scaling Configuration

The production configuration supports:
- **Multiple Replicas**: 2 replicas for the auth_api service
- **Resource Limits**:
  - Auth API: 2.0 CPU cores, 2GB memory (limits), 1.0 CPU core, 1GB memory (reservations)
  - PostgreSQL: 1.0 CPU core, 1GB memory (limits), 0.5 CPU core, 512MB memory (reservations)
  - Redis: 0.5 CPU core, 512MB memory (limits), 0.2 CPU core, 256MB memory (reservations)
- **Rolling Updates**: Parallelism of 1 with 10-second delays
- **Restart Policies**: Automatic restart with exponential backoff

### Environment Configuration

Production environment should include:

```bash
# Database (use production values)
DB_HOST=your-db-host
DB_PORT=5432
DB_USER=auth_user
DB_PASSWORD=secure-password
DB_TABLE=auth

# Redis (use production values)
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_DB=0

# JWT (use a strong, randomly generated key)
SECRET_KEY=your-very-secure-secret-key-here

# SSL (point to your production certificates)
SSL_CERTFILE=/path/to/your/cert.pem
SSL_KEYFILE=/path/to/your/key.pem
```

### Health Monitoring

The service includes health check endpoints:
- **Health Check**: `GET /health` - Returns service status
- **Docker Health Check**: Built into the Docker image

### Scaling

For production scaling:
- Use multiple workers: `--workers 4`
- Consider load balancing multiple instances
- Monitor Redis and PostgreSQL performance

## License

This project is licensed under the APGL-3.0 License - see the [LICENSE](LICENSE) file for details.
