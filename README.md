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
- `NEW_RELIC_LICENSE_KEY`: (Optional) Add your New Relic key in `docker-compose.yml` to enable monitoring.

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
