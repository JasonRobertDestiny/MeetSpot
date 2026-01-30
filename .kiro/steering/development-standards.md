# Development Standards & Best Practices

## Code Style & Formatting

### Python Standards
- **Indentation**: 4 spaces (never tabs)
- **Type hints**: Required everywhere - functions, variables, class attributes
- **Naming conventions**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `SCREAMING_SNAKE_CASE`
  - Private methods: `_leading_underscore`
- **Function length**: Keep under ~50 lines for readability
- **Data structures**: Prefer dataclasses for structured payloads over dictionaries

### HTML/CSS Standards
- **Class naming**: BEM-like convention (`meetspot-header__title`, `card--featured`)
- **Colors**: Always use design tokens from `static/css/design-tokens.css`
- **Inline styles**: Minimize usage, only for generated HTML in `workspace/js_src/`
- **Responsive design**: Mobile-first approach with progressive enhancement
- **Accessibility**: All interactive elements must be keyboard accessible

### JavaScript Standards
- **ES6+**: Use modern JavaScript features
- **Async/await**: Prefer over Promise chains
- **Error handling**: Always wrap API calls in try-catch blocks
- **DOM manipulation**: Use semantic HTML and ARIA attributes

## Quality Gates

### Pre-commit Requirements
All of these must pass before opening a PR:

```bash
# Code formatting
black .

# Linting
ruff check .

# Type checking
mypy app/

# Test coverage
pytest --cov=app tests/
# Target: ≥80% coverage for app/ package
```

### Testing Standards
- **Test organization**: Place tests in `tests/` using `test_<feature>.py` naming
- **Test types**:
  - Unit tests: Individual functions and classes
  - Integration tests: FastAPI routes + tool layer helpers
  - SEO tests: Meta tags, schema.org, sitemap validation
- **Fixtures**: Create reusable fixtures for database, API clients, mock data
- **Coverage**: Maintain ≥80% coverage for the `app/` package
- **Focus areas**: Prioritize testing caching, concurrency, and SEO logic

## Logging Standards

### Structured Logging
Use `app/logger.py` for all logging needs:

```python
from app.logger import logger

# Good: Structured logging with context
logger.info("geo_center_calculated", extra={
    "center_lat": 39.9042,
    "center_lng": 116.4074,
    "locations_count": 3,
    "processing_time": 1.2
})

# Bad: Unstructured string logging
logger.info("Calculated center at 39.9042, 116.4074")
```

### Log Levels
- **DEBUG**: Detailed diagnostic information
- **INFO**: General operational messages
- **WARNING**: Something unexpected but recoverable
- **ERROR**: Error conditions that don't stop execution
- **CRITICAL**: Serious errors that may abort execution

## Performance Guidelines

### Memory Management
- **Concurrency**: Respect `MAX_CONCURRENT_REQUESTS = 3` semaphore
- **Caching**: Use LRU cache with reasonable limits (30 geocodes, 15 POI searches)
- **Cleanup**: Call `gc.collect()` after memory-intensive operations
- **Agent mode**: Currently disabled to save memory on Render free tier

### Async Best Practices
- **All I/O async**: Use aiohttp, aiofiles, async database operations
- **Concurrent operations**: Use `asyncio.gather()` for parallel API calls
- **Error handling**: Always handle async exceptions properly
- **Session management**: Reuse HTTP sessions, close properly

### Caching Strategy
- **HTTP caching**: Set appropriate Cache-Control headers
  - Immutable assets: 1 year
  - Images: 30 days
  - Dynamic content: no-cache
- **Application caching**: Use LRU cache for expensive operations
- **Database caching**: Cache frequently accessed data

## Security Standards

### API Security
- **Authentication**: Use JWT tokens for protected endpoints
- **Rate limiting**: Apply appropriate limits (default 60/minute)
- **Input validation**: Validate all inputs using Pydantic models
- **CORS**: Configure appropriately for production
- **Environment variables**: Never hardcode secrets, use `.env` files

### Data Protection
- **PII handling**: Mask phone numbers in logs and responses
- **Token security**: Use secure JWT signing, appropriate expiration
- **Database**: Use parameterized queries (SQLAlchemy ORM handles this)
- **File uploads**: Validate file types and sizes if implemented

## Configuration Management

### Environment Variables
Required variables:
```bash
AMAP_API_KEY              # Required: Amap API key
```

Optional variables:
```bash
AMAP_SECURITY_JS_CODE     # Amap JS security code
AMAP_JS_API_KEY           # Amap JS API key
LLM_API_KEY               # LLM API key
LLM_API_BASE              # LLM base URL
LLM_MODEL                 # LLM model name
OPENAI_API_KEY            # Alternative OpenAI key
PORT                      # Server port (default 8000)
LOG_LEVEL                 # Logging level
```

### Configuration Hierarchy
1. Environment variables (highest priority)
2. `config/config.toml` file
3. `config/config.toml.example` (fallback)
4. Hardcoded defaults (lowest priority)

### Adding New Configuration
1. Add to appropriate settings class in `app/config.py`
2. Update `AppConfig` model
3. Add environment variable support
4. Update `config/config.toml.example`
5. Document in README.md

## Error Handling

### Exception Handling
- **Custom exceptions**: Use classes from `app/exceptions.py`
- **HTTP errors**: Return appropriate status codes with meaningful messages
- **Async exceptions**: Always handle in async contexts
- **Logging**: Log errors with context for debugging

### API Error Responses
```python
# Good: Structured error response
{
    "success": false,
    "error": "geocoding_failed",
    "message": "无法解析地址: 北京市朝阳区",
    "details": {
        "address": "北京市朝阳区",
        "provider": "amap"
    }
}
```

## Documentation Standards

### Code Documentation
- **Docstrings**: Use Google-style docstrings for all public functions/classes
- **Type hints**: Comprehensive type annotations
- **Comments**: Explain complex business logic, not obvious code
- **README**: Keep up-to-date with setup instructions and API documentation

### API Documentation
- **FastAPI**: Automatic OpenAPI/Swagger documentation
- **Endpoint descriptions**: Clear, concise descriptions of what each endpoint does
- **Request/response examples**: Provide realistic examples
- **Error codes**: Document all possible error responses