# AI Derma Diagnosis Server - Copilot Instructions

## Architecture Overview

This is a FastAPI-based dermatology diagnosis server following a clean architecture pattern with clear separation of concerns:

- **API Layer** (`app/api/v1/`): FastAPI routers with versioned endpoints
- **Core Layer** (`app/core/`): Configuration and shared utilities using Pydantic Settings
- **Service Layer** (`app/services/`): Business logic, especially authentication with JWT + bcrypt
- **CRUD Layer** (`app/crud/`): Database access functions using SQLAlchemy ORM
- **Models** (`app/models/`): SQLAlchemy ORM models extending `Base` from `app.db.base`
- **Schemas** (`app/schemas/`): Pydantic models for request/response validation

## Key Patterns & Conventions

### Database Integration

- **Connection**: Uses MySQL with PyMySQL driver via SQLAlchemy
- **Session Management**: Dependency injection pattern with `get_db()` from `app.db.session`
- **Table Creation**: Auto-creates tables in `main.py` with `Base.metadata.create_all(bind=engine)`
- **ORM Models**: All inherit from `Base` in `app.db.base`, use declarative style

### Authentication Flow

- **JWT Implementation**: Uses PyJWT (not python-jose) with HS256 algorithm
- **Password Security**: bcrypt hashing via passlib with `CryptContext`
- **Token Endpoint**: OAuth2 compatible at `/api/v1/users/token` expecting form-data
- **Dependencies**: `get_current_user()` validates Bearer tokens for protected routes

### API Structure

- **Versioning**: All endpoints under `/api/v1/` prefix with version-specific routers
- **Router Registration**: Include routers in `main.py` with consistent prefix/tags pattern
- **Response Models**: Use Pydantic schemas with `from_attributes = True` for ORM compatibility
- **Error Handling**: HTTPException with proper status codes and detail messages

## Development Workflows

### Environment Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run with Docker Compose (includes MySQL)
docker-compose up

# Local development server
uvicorn app.main:app --reload
```

### Database Operations

- **Configuration**: Environment variables via Pydantic Settings in `app.core.config`
- **Migrations**: Currently uses `create_all()` - consider adding Alembic for production
- **Connection String**: MySQL format: `mysql+pymysql://user:pass@host:port/db`

### Adding New Features

1. **Model**: Create SQLAlchemy model in `app/models/`
2. **Schema**: Define Pydantic models in `app/schemas/`
3. **CRUD**: Add database functions in `app/crud/`
4. **Router**: Create API endpoints in `app/api/v1/`
5. **Register**: Include router in `main.py`

## Project-Specific Notes

- **Korean Comments**: Mix of Korean and English comments - maintain existing language patterns
- **String Lengths**: User model uses `String(50)` for username, `String(255)` for hashed_password
- **Token Expiry**: Default 30 minutes configured in settings
- **Docker Ready**: MySQL container pre-configured with sample credentials
- **No Dependencies Directory**: Uses direct imports instead of dependency injection modules

## Security Considerations

- JWT secret key should be environment-specific (currently hardcoded)
- Database credentials exposed in docker-compose.yml for development
- OAuth2PasswordBearer expects form-data format for login requests
