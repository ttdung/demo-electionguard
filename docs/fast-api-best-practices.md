# FastAPI Best Practices Reference

Based on: https://github.com/zhanymkanov/fastapi-best-practices

## 1. Project Structure

### Organize by Domain/Feature, Not by File Type

Instead of grouping all models, all schemas, or all routers together, organize your code by feature/domain:

```
src/
├── auth/
│   ├── router.py       # auth endpoints
│   ├── schemas.py      # auth Pydantic models
│   ├── models.py       # auth database models
│   ├── service.py      # auth business logic
│   ├── dependencies.py # auth-specific dependencies
│   ├── constants.py    # auth constants
│   ├── config.py       # auth configuration
│   ├── exceptions.py   # auth exceptions
│   └── utils.py        # auth utilities
├── users/
│   ├── router.py
│   ├── schemas.py
│   └── ...
└── payments/
    ├── router.py
    ├── schemas.py
    └── ...
```

## 2. Async/Await Best Practices

### Use Async for I/O Operations
- Prefer `async def` for routes that perform I/O operations (database, external APIs)
- Use `await` for all async operations to avoid blocking

### Avoid Blocking in Async Routes
```python
# ❌ Bad - blocks the event loop
async def get_data():
    time.sleep(1)  # Blocking!
    return data

# ✅ Good - non-blocking
async def get_data():
    await asyncio.sleep(1)  # Non-blocking
    return data
```

### Handle Sync Operations Properly
```python
# For sync SDK/libraries in async routes
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

async def call_sync_sdk():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, sync_sdk_function, param)
    return result
```

## 3. Pydantic Model Best Practices

### Create Custom Base Model
```python
from pydantic import BaseModel, ConfigDict

class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True,  # Strip whitespace from strings
        use_enum_values=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )
```

### Rich Validation Features
```python
from pydantic import BaseModel, Field, EmailStr, constr, validator
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"

class UserCreate(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    age: int = Field(..., ge=18, le=120, description="User age must be 18-120")
    role: UserRole = UserRole.USER

    @validator("username")
    def validate_username(cls, v):
        if v.lower() in ["admin", "root"]:
            raise ValueError("Reserved username")
        return v
```

## 4. Dependency Injection Patterns

### Validate Against Database
```python
async def valid_user_id(
    user_id: int = Path(...),
    db: AsyncSession = Depends(get_db)
) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.get("/users/{user_id}")
async def get_user(user: User = Depends(valid_user_id)):
    return user
```

### Chain Dependencies
```python
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Validate token and return user
    pass

async def get_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise HTTPException(400, "Inactive user")
    return user

async def get_admin_user(user: User = Depends(get_active_user)) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(403, "Not an admin")
    return user
```

### Leverage Request-Scoped Caching
```python
# Dependencies are cached within a single request
async def get_settings() -> Settings:
    print("Loading settings...")  # Called only once per request
    return load_settings()

@router.get("/endpoint1")
async def endpoint1(settings: Settings = Depends(get_settings)):
    # First call loads settings
    pass

@router.get("/endpoint2")
async def endpoint2(
    settings1: Settings = Depends(get_settings),  # Cached
    settings2: Settings = Depends(get_settings),  # Cached
):
    # settings1 and settings2 are the same object
    pass
```

## 5. Error Handling

### Custom Exception Classes
```python
class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class UserNotFoundException(DomainException):
    """Raised when user is not found"""
    pass

class InvalidCredentialsException(DomainException):
    """Raised when credentials are invalid"""
    pass
```

### Global Exception Handlers
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    return JSONResponse(
        status_code=400,
        content={"error": exc.__class__.__name__, "message": str(exc)}
    )

@app.exception_handler(UserNotFoundException)
async def user_not_found_handler(request: Request, exc: UserNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"error": "USER_NOT_FOUND", "message": str(exc)}
    )
```

## 6. Service Layer Pattern

### Separate Business Logic from Routes
```python
# ❌ Bad - business logic in route
@router.post("/users")
async def create_user(data: UserCreate, db: Session = Depends(get_db)):
    # Validation logic
    if await db.query(User).filter_by(email=data.email).first():
        raise HTTPException(400, "Email taken")

    # Password hashing
    hashed = hash_password(data.password)

    # Database operation
    user = User(**data.dict(), password=hashed)
    db.add(user)
    await db.commit()

    # Send email
    await send_welcome_email(user.email)

    return user

# ✅ Good - logic in service layer
@router.post("/users")
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(data)

# service.py
class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, data: UserCreate) -> User:
        await self._validate_email_unique(data.email)
        user = await self._create_user_record(data)
        await self._send_welcome_email(user.email)
        return user
```

## 7. Configuration Management

### Environment-Specific Settings
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "FastAPI App"
    debug: bool = False
    database_url: str
    redis_url: str
    secret_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

### Modular Configuration
```python
# auth/config.py
class AuthConfig(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_prefix = "AUTH_"  # AUTH_JWT_SECRET, AUTH_JWT_ALGORITHM

# payments/config.py
class PaymentConfig(BaseSettings):
    stripe_api_key: str
    stripe_webhook_secret: str

    class Config:
        env_prefix = "PAYMENT_"  # PAYMENT_STRIPE_API_KEY
```

## 8. Testing Best Practices

### Use Pytest Fixtures
```python
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.fixture
async def client(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def db_session():
    async with async_session() as session:
        yield session
        await session.rollback()

@pytest.fixture
async def auth_client(client, test_user):
    token = create_token(test_user)
    client.headers["Authorization"] = f"Bearer {token}"
    return client
```

### Test Different Layers
```python
# Test routes
async def test_create_user_route(client: AsyncClient):
    response = await client.post("/users", json={...})
    assert response.status_code == 201

# Test service layer
async def test_user_service(db_session: AsyncSession):
    service = UserService(db_session)
    user = await service.create_user(UserCreate(...))
    assert user.id is not None

# Test dependencies
async def test_valid_user_dependency(db_session: AsyncSession):
    user = await create_test_user(db_session)
    result = await valid_user_id(user.id, db_session)
    assert result.id == user.id
```

## 9. Performance Optimization

### Use Database Connection Pooling
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,   # Recycle connections after 1 hour
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)
```

### Implement Caching
```python
from functools import lru_cache
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost")

async def get_user_cached(user_id: int) -> User:
    # Check cache
    cached = await redis_client.get(f"user:{user_id}")
    if cached:
        return User.parse_raw(cached)

    # Fetch from database
    user = await get_user_from_db(user_id)

    # Cache for 1 hour
    await redis_client.setex(
        f"user:{user_id}",
        3600,
        user.json()
    )
    return user
```

### Use Background Tasks
```python
from fastapi import BackgroundTasks

@router.post("/users")
async def create_user(
    data: UserCreate,
    background_tasks: BackgroundTasks,
    service: UserService = Depends()
):
    user = await service.create_user(data)

    # Non-critical tasks in background
    background_tasks.add_task(send_welcome_email, user.email)
    background_tasks.add_task(log_user_creation, user.id)

    return user
```

## 10. API Design Best Practices

### RESTful Resource Naming
- Use plural nouns for collections: `/users`, `/products`
- Use path parameters for specific resources: `/users/{user_id}`
- Use query parameters for filtering: `/users?status=active&limit=10`
- Use proper HTTP methods: GET (read), POST (create), PUT (replace), PATCH (partial update), DELETE (remove)

### Consistent Response Format
```python
class ResponseModel(BaseModel):
    success: bool = True
    data: Any = None
    error: str | None = None
    timestamp: datetime = Field(default_factory=datetime.now)

class PaginatedResponse(ResponseModel):
    data: list[Any]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
```

### Version Your API
```python
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")

app.include_router(v1_router)
app.include_router(v2_router)
```

## 11. Security Best Practices

### Rate Limiting
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/login")
@limiter.limit("5/minute")
async def login(request: Request, credentials: LoginSchema):
    # Login logic
    pass
```

### Input Validation and Sanitization
```python
from pydantic import BaseModel, validator
import bleach

class CommentCreate(BaseModel):
    content: str

    @validator("content")
    def sanitize_html(cls, v):
        # Remove dangerous HTML
        return bleach.clean(v, tags=[], strip=True)
```

### Secure Headers
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.example.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## 12. Logging and Monitoring

### Structured Logging
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        return json.dumps(log_data)

# Configure logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Request ID Middleware
```python
import uuid
from fastapi import Request

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

## Summary

These best practices help create maintainable, scalable, and secure FastAPI applications. Key principles:

1. **Organize by domain** - Group related functionality together
2. **Use async properly** - Don't block the event loop
3. **Leverage Pydantic** - For robust data validation
4. **Implement service layer** - Separate business logic from routes
5. **Handle errors gracefully** - Custom exceptions and handlers
6. **Use dependencies effectively** - For validation and code reuse
7. **Configure properly** - Environment-specific settings
8. **Test thoroughly** - Multiple layers of testing
9. **Optimize performance** - Caching, pooling, background tasks
10. **Secure your API** - Rate limiting, validation, secure headers
