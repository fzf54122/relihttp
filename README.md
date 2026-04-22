# relihttp

<div align="center">

**A production-ready, reliable HTTP client for Python**

**English** | [简体中文](README-ZH.md)

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Requests](https://img.shields.io/badge/Requests-2.0+-green.svg)](https://docs.python-requests.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)](https://github.com/fzf54122/relihttp)

[📖 Quick Start](#-quick-start) • [✨ Features](#-features) • [🧰 Development](#-development-with-uv) • [🏗️ Architecture](#-architecture) • [🔧 Configuration](#-configuration) • [🤝 Contributing](#-contributing)

</div>

## 🌟 Why choose relihttp?

relihttp is a lightweight HTTP client built on `requests` with reliability features enabled by default. It provides a policy-based design that makes behaviors easy to customize or replace.

<div align="center">

| 🎯 **Reliability by Default** | ⚡ **Fast Development** | 🛡️ **Customizable** | 📊 **Structured Logging** |
|:---:|:---:|:---:|:---:|
| Built-in timeouts, retries, and rate limiting | Simple API with sensible defaults | Policy-based architecture | Standard logging with request/response details |

</div>

## Status

Alpha (v0.1.0). APIs may change.

## ✨ Core Features

### 🔧 Reliability Controls
- **Timeout Control** - Global and per-request timeout settings
- **Smart Retries** - Retry policy for safe methods by default
- **Exponential Backoff** - With jitter to prevent thundering herds
- **Network Resilience** - Retries on network errors and select HTTP status codes
- **Circuit Breaker** - Prevent cascading failures under error bursts
- **Idempotency Keys** - Safe retries for non-idempotent methods

### 📦 Rate Limiting
- **Token Bucket Algorithm** - Smooth rate limiting
- **Flexible Modes** - `sleep` (wait for tokens) or `raise` (fail fast)
- **Per-Client Configuration** - Easy to adjust for different endpoints

### 📝 Logging & Observability
- **Structured Logging** - Standard `logging` module integration
- **Rich Context** - Request ID, method, URL, status, and timing information
- **Event Types** - `http.request`, `http.response`, `http.error` events
- **Tracing Headers** - Inject request/trace IDs for end-to-end tracking

#### Example Usage
```python
import logging
from relihttp import Client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

client = Client()
response = client.get("https://api.example.com/users")
```

#### Log Output
```
2026-02-03 14:30:00 - relihttp - INFO - event=http.request request_id=abc123 method=GET url=https://api.example.com/users
2026-02-03 14:30:00 - relihttp - INFO - event=http.response request_id=abc123 status_code=200 elapsed_ms=150
```

The structured logging format makes it easy to integrate with monitoring systems like ELK, Loki, or APM tools for better observability and faster issue debugging.

### 🏗️ Extensible Architecture
- **Policy-Based Design** - Easy to add or replace behaviors
- **Pluggable Transport** - Defaults to `requests`, but customizable
- **Middleware Hooks** - Before/after request and retry decision callbacks

### 🎨 Developer Experience
- **Familiar API** - Built on `requests` interface
- **Per-Request Overrides** - Customize settings for individual requests
- **Type Hints** - Full Python type annotations support
- **Clear Documentation** - Comprehensive guides and examples
- **AsyncIO Support** - Async client and transport (optional `aiohttp`)

## Installation

```bash
pip install relihttp
```

## 🧰 Development with uv

`uv` is the recommended package manager for development. It provides faster installation and better dependency management.

### Install uv

```bash
# Install uv (if not already installed)
pip install uv
```

### Common Commands

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Install dependencies
uv install

# Install with development dependencies
uv install -e .[dev]

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=relihttp

# Format code with ruff
uv run ruff format

# Lint code with ruff
uv run ruff check

# Type check with mypy
uv run mypy

# Build the package
uv build

# Clean up
uv clean
```

## 📦 Packaging & Publish

### Build locally

```bash
# Build sdist and wheel into dist/
uv build
```

### Publish to PyPI

```bash
# 1) Create API token on PyPI and export it
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-***"

# 2) Upload
python -m pip install twine
twine upload dist/*
```

### Publish to TestPyPI (recommended first)

```bash
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-***"

python -m pip install twine
twine upload --repository testpypi dist/*
```

## 🛠️ Technology Stack

| Component | Technology | Version |
|-----------|------------|---------|
| **Core HTTP Client** | requests | 2.0+ |
| **Python Version** | Python | 3.9+ |
| **Logging** | Standard `logging` module | - |
| **Architecture** | Policy-based middleware | - |

## 🚀 Quick Start (Sync)

```python
from relihttp import AbstractClient, ClientTypeEnum

client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    base_url="https://api.example.com",
    timeout=3.0,
    retry="safe",
    max_retries=3,
    rate_limit=100,
)

resp = client.get("/users")
print(resp.json())
```

Per-request overrides:

```python
client.post("/pay", json={"amount": 10}, timeout=1.5, max_retries=1)
```

## ⚡ Async Quick Start

```python
import asyncio
from relihttp import AbstractClient, ClientTypeEnum

async def main() -> None:
    client = AbstractClient.create_client(
        ClientTypeEnum.ASYNC,
        base_url="https://api.example.com",
        timeout=3.0,
        retry="safe",
        max_retries=3,
    )
    async with client:
        resp = await client.get("/users")
        print(resp.text)

asyncio.run(main())
```

## 🎯 AbstractClient Usage

`AbstractClient` provides a factory method to create either sync or async clients based on the specified mode:

```python
from relihttp import AbstractClient, ClientTypeEnum

# Create a sync client
sync_client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    base_url="https://api.example.com",
    timeout=3.0,
    max_retries=3
)

# Create an async client
async def main() -> None:
    async_client = AbstractClient.create_client(
        ClientTypeEnum.ASYNC,
        base_url="https://api.example.com",
        timeout=3.0,
        max_retries=3
    )
    async with async_client:
        resp = await async_client.get("/users")
        print(resp.text)

# Usage example
sync_response = sync_client.get("/health")
print(sync_response.status_code)
```

## 🔧 Usage Examples

### Sync Client (Basic)

```python
from relihttp import AbstractClient, ClientTypeEnum

client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    base_url="https://api.example.com"
)
resp = client.get("/health")
print(resp.status_code)
```

### Sync Client (Custom Policies)

```python
from relihttp import AbstractClient, ClientTypeEnum
from relihttp.policies.circuit import CircuitBreakerPolicy
from relihttp.policies.idempotency import IdempotencyPolicy
from relihttp.policies.tracing import TracingPolicy
from relihttp.policies.timeout import TimeoutPolicy
from relihttp.policies.retry import RetryPolicy
from relihttp.policies.logger import LoggingPolicy
from relihttp.policies.rate_limit import RateLimitPolicy

client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    policies=[
        TimeoutPolicy(timeout=3.0),
        RetryPolicy(max_retries=3, retry="safe"),
        RateLimitPolicy(rate_limit=50, burst=100, mode="sleep"),
        CircuitBreakerPolicy(window_size=20, failure_ratio=0.5, min_requests=10),
        IdempotencyPolicy(),
        TracingPolicy(request_id_header="X-Request-ID", trace_id_header="X-Trace-ID"),
        LoggingPolicy(),
    ]
)

resp = client.post("/payments", json={"amount": 10})
print(resp.status_code)
```

### Async Client (Basic)

```python
import asyncio
from relihttp import AbstractClient, ClientTypeEnum

async def main() -> None:
    client = AbstractClient.create_client(ClientTypeEnum.ASYNC)
    async with client:
        resp = await client.get("https://example.com")
        print(resp.status_code)

asyncio.run(main())
```

### Async Client (Per-request Override)

```python
import asyncio
from relihttp import AbstractClient, ClientTypeEnum

async def main() -> None:
    client = AbstractClient.create_client(
        ClientTypeEnum.ASYNC,
        base_url="https://api.example.com"
    )
    async with client:
        resp = await client.post("/pay", json={"amount": 10}, timeout=1.5, max_retries=1)
        print(resp.text)

asyncio.run(main())
```

### Async Client (Custom Transport)

```python
import asyncio
from relihttp import AbstractClient, ClientTypeEnum
from relihttp.transport.aiohttp import AiohttpTransport

async def main() -> None:
    transport = AiohttpTransport()
    client = AbstractClient.create_client(
        ClientTypeEnum.ASYNC,
        transport=transport
    )
    async with client:
        resp = await client.get("https://example.com")
        print(resp.status_code)

asyncio.run(main())
```

## 🔧 Configuration

Enable additional reliability features with simple flags:

```python
from relihttp import AbstractClient, ClientTypeEnum

client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    base_url="https://api.example.com",
    circuit_breaker=True,
    idempotency=True,
    trace=True,
)
```

### Circuit Breaker (Advanced)

```python
from relihttp import AbstractClient, ClientTypeEnum
from relihttp.policies.circuit import CircuitBreakerPolicy
from relihttp.policies.timeout import TimeoutPolicy
from relihttp.policies.retry import RetryPolicy
from relihttp.policies.logger import LoggingPolicy

client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    policies=[
        TimeoutPolicy(timeout=3.0),
        RetryPolicy(max_retries=3, retry="safe"),
        LoggingPolicy(),
        CircuitBreakerPolicy(failure_threshold=3, recovery_timeout=10.0),
    ]
)
```

### Idempotency Key (Advanced)

```python
from relihttp import AbstractClient, ClientTypeEnum
from relihttp.policies.idempotency import IdempotencyPolicy
from relihttp.policies.timeout import TimeoutPolicy
from relihttp.policies.retry import RetryPolicy
from relihttp.policies.logger import LoggingPolicy

client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    policies=[
        TimeoutPolicy(timeout=3.0),
        RetryPolicy(max_retries=3, retry="safe"),
        LoggingPolicy(),
        IdempotencyPolicy(header_name="Idempotency-Key"),
    ]
)
```

### Tracing & Request ID (Advanced)

```python
from relihttp import AbstractClient, ClientTypeEnum
from relihttp.policies.tracing import TracingPolicy
from relihttp.policies.timeout import TimeoutPolicy
from relihttp.policies.retry import RetryPolicy
from relihttp.policies.logger import LoggingPolicy

client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    policies=[
        TimeoutPolicy(timeout=3.0),
        RetryPolicy(max_retries=3, retry="safe"),
        LoggingPolicy(),
        TracingPolicy(request_id_header="X-Request-ID", trace_id_header="X-Trace-ID"),
    ]
)
```

### Async Client (AsyncIO)

```python
 # Install async support:
 # pip install relihttp[async]
 
import asyncio
from relihttp import AbstractClient, ClientTypeEnum

async def main() -> None:
    client = AbstractClient.create_client(ClientTypeEnum.ASYNC)
    async with client:
        resp = await client.get("https://example.com")
        print(resp.status_code)

asyncio.run(main())
```

## Retry Behavior

Default `retry="safe"` only retries idempotent methods: `GET`, `HEAD`, `OPTIONS`, `PUT`, `DELETE`.  
Retries are triggered for network errors from `requests` and for HTTP status codes `500`, `502`, `503`, `504`, `429`.

`max_retries` is the maximum total attempts (including the first try).

Custom policy example:

```python
from relihttp import AbstractClient, ClientTypeEnum
from relihttp.policies.retry import RetryPolicy
from relihttp.policies.timeout import TimeoutPolicy
from relihttp.policies.logger import LoggingPolicy

client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    policies=[
        TimeoutPolicy(timeout=2.0),
        RetryPolicy(max_retries=5, retry="all", retry_on_status=[500, 502, 503]),
        LoggingPolicy(),
    ]
)
```

## Rate Limiting

`rate_limit` is tokens per second. By default, the limiter blocks until a token is available.  
You can switch to `raise` mode to fail fast; it raises `RateLimitedError`.

```python
from relihttp import AbstractClient, ClientTypeEnum
from relihttp.policies.rate_limit import RateLimitPolicy
from relihttp.policies.timeout import TimeoutPolicy
from relihttp.policies.retry import RetryPolicy
from relihttp.policies.logger import LoggingPolicy

client = AbstractClient.create_client(
    ClientTypeEnum.SYNC,
    policies=[
        TimeoutPolicy(timeout=3.0),
        RetryPolicy(max_retries=3),
        RateLimitPolicy(rate_limit=50, burst=100, mode="raise"),
        LoggingPolicy(),
    ]
)
```

## Logging

The library emits structured logs through the `relihttp` logger with event names:

- `http.request`
- `http.response`
- `http.error`

Each record includes fields like `request_id`, `method`, `url`, `attempt`, `status_code`, and `elapsed_ms`. Configure handlers and formatters via the standard `logging` module.

## Policies and Transport

`Client(policies=...)` uses exactly the policies you pass; defaults are not added automatically.  
If you override policies, include `TimeoutPolicy`, `RetryPolicy`, and `LoggingPolicy` explicitly as needed.

The default transport is `RequestsTransport`, built on `requests.Session`. You can implement your own transport by subclassing `Transport` and passing it to `Client(transport=...)`.

## 📁 Project Structure

```
relihttp/
  __init__.py                 # Package initialization
  client/                     # Client implementations
    __init__.py               # Client package initialization
    BaseClient.py             # Base client class
    SyncClient.py             # Sync Client class
    AsyncClient.py            # Async Client (AsyncIO)
    __init__.py               # Exports AbstractClient and ClientTypeEnum
  models.py                   # Data models
  transport/                  # Transport layer implementations
    base.py                  # Transport base class
    requests.py              # Requests-based transport
    async_base.py            # Async transport base class
    aiohttp.py               # aiohttp-based transport
  policies/                   # Policy implementations
    base.py                  # Policy base class
    retry.py                 # Retry policy
    timeout.py               # Timeout policy
    rate_limit.py            # Rate limiting policy
    logger.py                # Logging policy
    circuit.py               # Circuit breaker policy
    idempotency.py           # Idempotency key support
    tracing.py               # Tracing support
  utils.py                    # Utility functions
tests/                        # Test suite
pyproject.toml               # Project configuration
README.md                    # English documentation
README-ZH.md                 # Chinese documentation
```

## 🔮 Roadmap (Planned)

- **OpenTelemetry Integration** - Standardized tracing propagation
- **More Transports** - httpx/urllib3 support

## 📋 Requirements

- Python 3.9+

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Run tests before submitting:

```bash
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 💡 Philosophy

**Reliability should be the default, not an afterthought.**

We believe that building resilient systems shouldn't require complex configuration or boilerplate code. relihttp provides reliability features out of the box, so you can focus on building your application rather than worrying about network failures or transient errors.