# Low-Level Design (LLD)

## Database Schema (PostgreSQL)

### Users Table
- `id` (SERIAL PRIMARY KEY): Unique user identifier.
- `username` (VARCHAR(255) UNIQUE NOT NULL): User's login name.
- `join_date` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Registration time.
*Index on `username`*

### Game Sessions Table
- `id` (SERIAL PRIMARY KEY): Session identifier.
- `user_id` (INT REFERENCES users(id) ON DELETE CASCADE): Foreign Key to Users.
- `score` (INT NOT NULL): Score achieved in the session.
- `game_mode` (VARCHAR(50) NOT NULL): Game type (e.g., 'survival', 'ranked').
- `timestamp` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Session time.
*Index on `user_id`*

### Leaderboard Table
- `id` (SERIAL PRIMARY KEY): Unique identifier.
- `user_id` (INT REFERENCES users(id) ON DELETE CASCADE): User identifier.
- `total_score` (INT NOT NULL): Accumulative score across all sessions.
- `rank` (INT): Optional, but dynamically calculated in Redis/Queries.
*Index on `total_score` (DESC)*

## Redis Keys
- **`leaderboard_scores`**: A Sorted Set (ZSET).
  - Member: `user_id` (String)
  - Score: `total_score` (Double)

## API Endpoints

### 1. Submit Score
- **Endpoint**: `POST /api/leaderboard/submit`
- **Request Body**:
    ```json
    {
        "user_id": 123,
        "score": 50,
        "game_mode": "survival"
    }
    ```
- **Logic**:
    1.  Validate input.
    2.  Start DB transaction.
    3.  Insert into `game_sessions`: `INSERT INTO game_sessions (user_id, score, game_mode) VALUES (...)`.
    4.  Update `leaderboard`:
        -   `INSERT INTO leaderboard (user_id, total_score) VALUES (...) ON CONFLICT (user_id) DO UPDATE SET total_score = leaderboard.total_score + EXCLUDED.score`.
    5.  Update Redis: `ZINCRBY leaderboard_scores score user_id`.
    6.  Commit transaction.
    7.  Return success.

### 2. Get Top Players
- **Endpoint**: `GET /api/leaderboard/top`
- **Response**:
    ```json
    {
        "top_players": [
            { "user_id": 123, "total_score": 1500, "rank": 1 },
            ...
        ]
    }
    ```
- **Logic**:
    1.  Try Redis: `ZREVRANGE leaderboard_scores 0 9 WITHSCORES`.
    2.  If data exists, return formatted list.
    3.  Else, query DB: `SELECT ... ORDER BY total_score DESC LIMIT 10`.
    4.  Populate Redis with results (optional, or rely on writes).
    5.  Return list.

### 3. Get User Rank
- **Endpoint**: `GET /api/leaderboard/rank/{user_id}`
- **Response**:
    ```json
    {
        "user_id": 123,
        "rank": 5,
        "total_score": 1200
    }
    ```
- **Logic**:
    1.  Try Redis:
        -   Rank: `ZREVRANK leaderboard_scores user_id`
        -   Score: `ZSCORE leaderboard_scores user_id`
    2.  If found, return rank + 1.
    3.  Else, query DB rank calculation (slow):
        -   `SELECT count(*) FROM leaderboard WHERE total_score > (SELECT total_score FROM leaderboard WHERE user_id = :uid)`
    4.  Update Redis with found score.
    5.  Return rank.

## Scalability Considerations

- **Redis**: Sorted sets provide exceptionally fast rank retrieval even with millions of users.
- **Asynchronous Processing**: FastAPI uses `asyncio` to handle high connection concurrency without blocking threads.
- **Write-Through Caching**: Ensures consistency between Redis and PostgreSQL.
- **Database Partitioning (Future)**: Could partition `game_sessions` by time or user_id hash if volume grows further.

## Monitoring

- **New Relic**:
  - APM (Application Performance Monitoring) to track request latency.
  - Custom metrics for cache hit rate.
  - Alerting on error rate > 1%.
