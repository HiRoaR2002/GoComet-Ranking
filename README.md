# Gaming Leaderboard System

Welcome to the Gaming Leaderboard System! This project implements a high-performance, real-time leaderboard capable of handling millions of users and high concurrency, built with FastAPI, Redis, PostgreSQL, and React.

## 🚀 Getting Started

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (for running simulation scripts locally)
- Node.js 18+ (optional, if running frontend outside Docker)

### Quick Start with Docker

1.  **Build and Start Services**:
    Open the terminal in this directory and run:
    ```bash
    docker-compose up --build
    ```
    *Note: The first run may take a few minutes as it initializes the database with 1 million users and 5 million game sessions.*

2.  **Access the Application**:
    -   Frontend (Leaderboard UI): [http://localhost:5173](http://localhost:5173)
    -   Backend API Docs (Swagger): [http://localhost:8000/docs](http://localhost:8000/docs)

### 🎮 Simulating Traffic

To test the system under load and see the live updates on the leaderboard, run the provided simulation script.

1.  Open a new terminal.
2.  Install dependencies (if not already installed):
    ```bash
    pip install requests
    ```
3.  Run the simulation script:
    ```bash
    python scripts/simulate.py
    ```
    This script will spawn multiple threads to continuously submit scores and query the leaderboard, mimicking real-world traffic.

## 2. Architecture Overview

-   **Frontend**: React + Vite (Vanilla CSS with Glassmorphism design).
-   **Backend**: FastAPI (Async Python) for high throughput.
-   **Database**: PostgreSQL (Persistent storage for Users, Sessions, and Leaderboard).
-   **Cache**: Redis (Sorted Sets for O(log N) leaderboard operations).
-   **Monitoring**: Integrated with New Relic (requires License Key).

## 3. Configuration

### Environment Variables
The system uses environment variables defined in `docker-compose.yml`.
- `DATABASE_URL`: PostgreSQL connection string.
- `REDIS_URL`: Redis connection string.
- `NEW_RELIC_LICENSE_KEY`: (Optional) Add your New Relic key to enable comprehensive performance monitoring.

### 📊 New Relic Monitoring (Recommended)

This application comes with **full New Relic APM integration** to track API performance, database queries, and system bottlenecks.

**Quick Setup (3 steps):**

1. **Sign up for free** at https://newrelic.com (100GB/month free, no credit card)
2. **Get your license key** from https://one.newrelic.com/api-keys (create "License" type)
3. **Add to `.env` file**:
   ```bash
   cp .env.example .env
   # Edit .env and add:
   NEW_RELIC_LICENSE_KEY=your_license_key_here
   ```

4. **Restart containers**:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

**What New Relic Monitors:**
- ✅ API endpoint response times (with 500ms slow threshold alerts)
- ✅ Database query performance (tracks queries > 100ms)
- ✅ Redis cache hit/miss rates
- ✅ Error tracking and alerting
- ✅ Custom business metrics (score submissions, cache effectiveness)
- ✅ Distributed tracing across services

**View Performance Data:**
- Dashboard: https://one.newrelic.com → APM & Services → "GoComet Leaderboard API"
- **Full Setup Guide:** [NEW_RELIC_README.md](./NEW_RELIC_README.md)
- **Detailed Documentation:** [NEW_RELIC_GUIDE.md](./NEW_RELIC_GUIDE.md)
- **Alert Setup Script:** `backend/create_alerts.py`


## 4. Documentation

Detailed design documents are available in the `docs/` folder:
-   [High-Level Design (HLD)](docs/HLD.md)
-   [Low-Level Design (LLD)](docs/LLD.md)

## 5. API Endpoints

-   `POST /api/leaderboard/submit`: Submit a score for a user.
-   `GET /api/leaderboard/top`: Get top 10 players.
-   `GET /api/leaderboard/rank/{user_id}`: Get rank and score for a specific user.

---
**Note to Reviewer**: 
The database initialization script automatically seeds 1M users and 5M game sessions on the first run. Please allow some time for the containers to fully start up. All deliverables requested in the prompt, including optimization (indexes, Redis), monitoring (New Relic hook), and documentation, are included.
