# High-Level Design (HLD)

## Overview
This document outlines the architecture for a high-performance, real-time gaming leaderboard system designed to handle millions of users and high concurrency. The system is built with a focus on low latency, scalability, and robust data integrity using FastAPI, PostgreSQL, and Redis.

## Architecture Diagram
(Conceptual)
[Client (Game/Web)] -> [Load Balancer] -> [API Server (FastAPI)] -> [Redis Cache] (Write-Through)
                                            |
                                            v
                                     [PostgreSQL Database] (Persistence)

## Key Components

1.  **Frontend (React + Vite)**:
    -   Provides a responsive UI for displaying the leaderboard.
    -   Features live updates using polling or WebSocket (initially polling for simplicity).
    -   Displays top 10 players and allows users to search for their rank.

2.  **Backend API (FastAPI)**:
    -   Handles authenticated requests for score submission and leaderboard retrieval.
    -   Implemented using async/await for non-blocking I/O.
    -   Validates input data using Pydantic models.

3.  **Data Storage (PostgreSQL)**:
    -   Primary source of truth for user data and game sessions.
    -   Stores structured data: `users`, `game_sessions`, `leaderboard`.
    -   Uses transactions to ensure atomicity of score updates.

4.  **Caching Layer (Redis)**:
    -   Stores the leaderboard using Sorted Sets (`ZSET`).
    -   Provides O(log N) complexity for rank retrieval and score updates.
    -   Acts as a write-through cache to the database for high-speed reads.

5.  **Monitoring (New Relic)**:
    -   Tracks API latency, throughput, and error rates.
    -   Monitors database query performance and Redis hit rates.

## Data Flow

### 1. Score Submission
1.  Client sends `POST /api/leaderboard/submit` with `user_id` and `score`.
2.  API validates the request.
3.  **Transaction Start**:
    -   Insert record into `game_sessions`.
    -   Upsert (Insert/Update) `total_score` in `leaderboard` table.
4.  **Cache Update**:
    -   `ZINCRBY` score in Redis `leaderboard_scores` sorted set.
5.  **Transaction Commit**:
    -   If any step fails, rollback database transaction.
6.  Return success response.

### 2. Get Top Leaderboard
1.  Client sends `GET /api/leaderboard/top`.
2.  API queries Redis `ZREVRANGE` (0-9) for top 10 users.
3.  If Redis is empty (cold start/failover), fallback to PostgreSQL query:
    -   `SELECT ... FROM leaderboard ORDER BY total_score DESC LIMIT 10`.
    -   Populate Redis with results.
4.  Return list of top players.

### 3. Get User Rank
1.  Client sends `GET /api/leaderboard/rank/{user_id}`.
2.  API queries Redis `ZREVRANK` and `ZSCORE`.
3.  If found, calculate rank (index + 1) and return.
4.  If not found in Redis, query PostgreSQL:
    -   `SELECT count(*) FROM leaderboard WHERE total_score > (SELECT total_score FROM leaderboard WHERE user_id = ?)`
    -   Update Redis with the user's score to cache subsequent requests.
5.  Return rank and score.
