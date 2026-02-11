-- Create Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Game Sessions table
CREATE TABLE IF NOT EXISTS game_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    score INT NOT NULL,
    game_mode VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Leaderboard table
CREATE TABLE IF NOT EXISTS leaderboard (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    total_score INT NOT NULL,
    rank INT
);

-- Add indexes for optimization
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_game_sessions_user_id ON game_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_leaderboard_total_score ON leaderboard(total_score DESC);

-- SEED DATA (Only runs if DB is fresh)
-- 1. Populate Users Table with 1 Million Records
-- This might take a few seconds/minutes
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM users LIMIT 1) THEN
        INSERT INTO users (username) 
        SELECT 'user_' || generate_series(1, 1000000);
    END IF;
END $$;

-- 2. Populate Game Sessions with 5 Million Random Records
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM game_sessions LIMIT 1) THEN
        INSERT INTO game_sessions (user_id, score, game_mode, timestamp)
        SELECT 
            floor(random() * 1000000 + 1)::int,
            floor(random() * 1000 + 10)::int,
            CASE WHEN random() > 0.5 THEN 'solo' ELSE 'team' END,
            NOW() - (random() * (interval '365 days'))
        FROM generate_series(1, 5000000);
    END IF;
END $$;

-- 3. Populate Initial Leaderboard from Sessions
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM leaderboard LIMIT 1) THEN
        INSERT INTO leaderboard (user_id, total_score, rank)
        SELECT user_id, SUM(score) as total_score, 0
        FROM game_sessions
        GROUP BY user_id;
    END IF;
END $$;
