from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..database import get_db, SessionLocal
from ..models import User, GameSession, LeaderboardEntry
from ..schemas import GameSessionCreate, LeaderboardResponse, UserRank
from ..cache import get_redis
from redis.asyncio import Redis
import json
import newrelic.agent
import time

router = APIRouter(
    prefix="/api/leaderboard",
    tags=["leaderboard"],
)

@router.post("/submit")
@newrelic.agent.function_trace(name='submit_score', group='Leaderboard')
async def submit_score(
    item: GameSessionCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    try:
        start_time = time.time()
        
        # Track custom event in New Relic
        newrelic.agent.record_custom_event('ScoreSubmission', {
            'user_id': item.user_id,
            'score': item.score,
            'game_mode': item.game_mode
        })
        
        # 1. Insert Game Session (with timing)
        db_start = time.time()
        new_session = GameSession(user_id=item.user_id, score=item.score, game_mode=item.game_mode)
        db.add(new_session)
        
        # 2. Update Leaderboard Table (Atomic increment/Insert)
        stmt = text("""
            INSERT INTO leaderboard (user_id, total_score, rank)
            VALUES (:uid, :score, 0)
            ON CONFLICT (user_id) 
            DO UPDATE SET total_score = leaderboard.total_score + EXCLUDED.total_score
        """)
        await db.execute(stmt, {"uid": item.user_id, "score": item.score})
        await db.commit()
        
        db_time = time.time() - db_start
        newrelic.agent.record_custom_metric('Custom/Database/SubmitScore', db_time)
        
        # 3. Update Redis (Write-through/Write-back)
        redis_start = time.time()
        await redis.zincrby("leaderboard_scores", item.score, str(item.user_id))
        redis_time = time.time() - redis_start
        newrelic.agent.record_custom_metric('Custom/Redis/UpdateScore', redis_time)
        
        total_time = time.time() - start_time
        newrelic.agent.record_custom_metric('Custom/Endpoint/SubmitScore/TotalTime', total_time)
        
        return {"message": "Score submitted successfully"}
    except Exception as e:
        await db.rollback()
        
        # Record error in New Relic
        newrelic.agent.record_custom_event('ScoreSubmissionError', {
            'user_id': item.user_id,
            'error': str(e)
        })
        
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top", response_model=LeaderboardResponse)
@newrelic.agent.function_trace(name='get_top_users', group='Leaderboard')
async def get_top_users(redis: Redis = Depends(get_redis), db: Session = Depends(get_db)):
    start_time = time.time()
    
    # Try getting from Redis
    redis_start = time.time()
    top_users_raw = await redis.zrevrange("leaderboard_scores", 0, 9, withscores=True)
    redis_time = time.time() - redis_start
    newrelic.agent.record_custom_metric('Custom/Redis/GetTopUsers', redis_time)
    
    if top_users_raw:
        # Cache hit
        newrelic.agent.record_custom_metric('Custom/Cache/TopUsers/Hit', 1)
        newrelic.agent.add_custom_attribute('cache_hit', True)
        
        # Format response
        result = []
        for i, (uid, score) in enumerate(top_users_raw):
            result.append({"user_id": int(uid), "total_score": int(score), "rank": i + 1})
        
        total_time = time.time() - start_time
        newrelic.agent.record_custom_metric('Custom/Endpoint/GetTopUsers/TotalTime', total_time)
        
        return {"top_players": result}
    
    # Cache miss - Fallback to DB
    newrelic.agent.record_custom_metric('Custom/Cache/TopUsers/Miss', 1)
    newrelic.agent.add_custom_attribute('cache_hit', False)
    
    db_start = time.time()
    top_entries = await db.execute(text("SELECT user_id, total_score FROM leaderboard ORDER BY total_score DESC LIMIT 10"))
    db_time = time.time() - db_start
    newrelic.agent.record_custom_metric('Custom/Database/GetTopUsers', db_time)
    
    result = []
    for i, row in enumerate(top_entries):
        # Populate Redis for next time
        await redis.zadd("leaderboard_scores", {str(row.user_id): row.total_score})
        result.append({"user_id": row.user_id, "total_score": row.total_score, "rank": i + 1})
    
    total_time = time.time() - start_time
    newrelic.agent.record_custom_metric('Custom/Endpoint/GetTopUsers/TotalTime', total_time)
        
    return {"top_players": result}

@router.get("/rank/{user_id}", response_model=UserRank)
@newrelic.agent.function_trace(name='get_user_rank', group='Leaderboard')
async def get_user_rank(user_id: int, redis: Redis = Depends(get_redis), db: Session = Depends(get_db)):
    start_time = time.time()
    
    # Add custom parameter for tracking
    newrelic.agent.add_custom_attribute('lookup_user_id', user_id)
    
    # Try Redis
    redis_start = time.time()
    rank = await redis.zrevrank("leaderboard_scores", str(user_id))
    score = await redis.zscore("leaderboard_scores", str(user_id))
    redis_time = time.time() - redis_start
    newrelic.agent.record_custom_metric('Custom/Redis/GetUserRank', redis_time)
    
    if rank is not None and score is not None:
        # Cache hit
        newrelic.agent.record_custom_metric('Custom/Cache/UserRank/Hit', 1)
        newrelic.agent.add_custom_attribute('cache_hit', True)
        
        total_time = time.time() - start_time
        newrelic.agent.record_custom_metric('Custom/Endpoint/GetUserRank/TotalTime', total_time)
        
        return {"user_id": user_id, "rank": rank + 1, "total_score": int(score)}
        
    # Cache miss - Fallback to DB
    newrelic.agent.record_custom_metric('Custom/Cache/UserRank/Miss', 1)
    newrelic.agent.add_custom_attribute('cache_hit', False)
    
    # Calculate rank via DB (expensive query - track it carefully)
    db_start = time.time()
    result = await db.execute(text("""
        SELECT total_score, 
        (SELECT COUNT(*) + 1 FROM leaderboard l2 WHERE l2.total_score > l1.total_score) as rank
        FROM leaderboard l1
        WHERE user_id = :uid
    """), {"uid": user_id})
    db_time = time.time() - db_start
    newrelic.agent.record_custom_metric('Custom/Database/GetUserRank', db_time)
    
    # Flag slow queries
    if db_time > 0.1:  # 100ms threshold
        newrelic.agent.record_custom_metric('Custom/SlowQuery/GetUserRank', db_time)
        newrelic.agent.add_custom_attribute('slow_query', True)
    
    row = result.first()
    if not row:
        newrelic.agent.record_custom_event('UserNotFound', {'user_id': user_id})
        raise HTTPException(status_code=404, detail="User not found")
         
    # Update Redis
    await redis.zadd("leaderboard_scores", {str(user_id): row.total_score})
    
    total_time = time.time() - start_time
    newrelic.agent.record_custom_metric('Custom/Endpoint/GetUserRank/TotalTime', total_time)
    
    return {"user_id": user_id, "rank": row.rank, "total_score": row.total_score}
