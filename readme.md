# Price Monitoring System

A comprehensive backend API and Dashboard for monitoring and querying product pricing data across multiple high-end fashion platforms (1stDibs, Fashionphile, Grailed). Built to satisfy complex data mapping, scraping orchestration, webhook push notifications, and cryptographic API Key validation.

## Tech Stack
- **FastAPI** (Web framework)
- **SQLAlchemy [asyncio] + aiosqlite** (Database ORM & SQLite Driver)
- **Jinja2 + Bootstrap 5 + Chart.js** (Server-Side Rendered Analytics Dashboard)
- **httpx & tenacity** (Async Web Scraper Requests & Webhook Push Engine)
- **Pydantic v2** (Strict Type Validation)
- **Pytest** (Asynchronous Test Suite)

---


## Local Development Setup

We recommend using **`uv`** (an extremely fast Python package manager) or standard `pip`. 

### 1. Create Virtual Environment and Install Dependencies
For Windows:
```bash
cd server
uv venv
source .venv/Scripts/activate
uv pip install -r requirements.txt
```

For mac/linux:
```bash
cd server
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Setup Configuration
Copy the default environment variables to a local `.env` file:
```bash
cp .env.example .env
```

### 3. Initialize Database & Generate Secure Defaults
```bash
python scripts/init_db.py
```
*This command executes the raw DB `create_all`, and explicitly plants a core Admin Key: `secret-entrupy-key`* inside the resulting `entrupy.db` SQlite backend. It also seeds the inital data from sample_products folder

### 4. Start the Application & Scrapers
Boot the application factory locally using Uvicorn:
```bash
uvicorn app.main:create_app --reload --host 0.0.0.0 --port 8000 --factory
```

## Exploring the Platform

### 1. The Interactive Dashboard
Navigate directly to **http://localhost:8000/** in your browser.
This boots the local `Jinja2` frontend GUI.

### 2. Run the Concurrent Scrapers (Ingestion)
Click the giant **"Refresh Data Now"** Button from the Homepage Dashboard.
- **Behind the scenes:** Javascript dynamically fires a `POST /api/v1/system/refresh` using the test `X-API-Key`.
- Python spins up `asyncio.gather()` executing all 3 scrapers mapped internally pointing to the `sample_products` directories. The dashboard redirects to refresh itself upon SQL commit.

### 3. API Usage
*Header Required: `X-API-Key: secret-entrupy-key`*
- **Read Products (Pagination):** `GET http://localhost:8000/api/v1/products/`  
- **Analytics:** `GET http://localhost:8000/api/v1/analytics/`
- **Audit Logging Events:** `GET http://localhost:8000/api/v1/events/`
- **Webhooks:** `POST http://localhost:8000/api/v1/webhooks/`

---

## Automated Testing

The robust async testing suite binds natively to an empty in-memory mapped representation utilizing `pytest_asyncio`. 

```bash
cd server
pytest -v
```


## Design Decisions (Assignment Requirements)

### 1. How does your price history scale? What happens at millions of rows?
**Approach & Rationale:**
- **Indexed Time-Series Data:** The `price_history` table uses a composite index `Index('ix_price_history_product_id_recorded_at', 'product_id', 'recorded_at')`. This guarantees $O(\log N)$ lookup performance when plotting charts or querying historical trends for a given product.
- **Append-Only Immutable Ledger:** Price updates do not modify historical rows; instead, they `INSERT` a new immutable snapshot. This prevents row locks from blocking concurrent reads.
- **Millions of Rows Consideration:** For >10M rows, the SQLite implementation would be swapped for Postgres (which SQLAlchemy Abstract Base Classes natively support). We would further partition the `price_history` table by `date` (e.g., monthly partitions) and introduce a materialized view for aggregations so that the primary endpoint calculations stay under 50ms.

### 2. How did you implement notification of price changes, and why that approach over alternatives?
**Approach & Rationale:**
- **Push Webhooks + HMAC-SHA256:** Subscribers register an endpoint URL and Secret Key. The system pushes HTTP POSTs signed with `X-Entrupy-Signature`.
- **Tenacity Exponential Backoff:** The HTTP delivery logic relies on `tenacity` (`@retry` with exponential backoff) for resilience against 429s/500s.
- **Non-Blocking Background Tasks:** Price shifts trigger `asyncio.create_task(dispatch_webhooks(...))` out-of-band. This ensures that the primary data ingestion flow is never blocked by a slow client webhook server.
- **Why this over alternatives?** Polling wastes API bandwidth. Webhooks are real-time, event-driven, and shift the computational load to the edge client while our retry engine ensures reliable "at-least-once" delivery.

### 3. How would you extend this system to 100+ data sources?
**Approach & Rationale:**
- **Distributed Task Queues (Celery/RabbitMQ):** Migrating from `asyncio.gather` in a single FastAPI container to a robust cluster of worker nodes. Each worker would consume `scrape_marketplace_X` messages.
- **Dynamic Scraper Registry & Rate Limiting:** We would utilize proxy rotation (e.g., BrightData), dynamic DOM-rendering (Playwright), and strict global concurrency limits. The `BaseScraper` class is already designed to be horizontally inherited.
- **Unified Normalization Layer:** Move field mapping from hardcoded logic into an external mapping configuration (e.g., JSON Schema mappings per domain) to drastically reduce the boilerplate needed to onboard site #101.

### 4. Known Limitations — what would you improve with more time?
- **Current Limitation:** Subscriptions evaluate the local `AsyncSession` across threads which can lead to bound errors on massive scale. We should refactor to utilize a message broker like Redis.
- **React Frontend:** The assignment suggested using Javascript/React. Given time constraints, I opted for Jinja2 Server-Side rendering. It is highly functional but lacks Client-Side state routing.
- **Authentication Extensibility:** `X-API-Key` is hardcoded to single strings per user. With more time, we would implement standard OAuth2 JWT provisioning.
- **Fake Async File Reading:** Because the dataset consisted of local `.json` files, `httpx` async fetch was simulated.

---

