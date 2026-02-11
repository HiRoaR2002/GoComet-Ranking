from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from ..database import get_db, SessionLocal
from ..models import User, GameSession, LeaderboardEntry
from ..schemas import GameSessionCreate, LeaderboardResponse, UserRank
from ..cache import get_redis
from redis.asyncio import Redis
import json

router = APIRouter(
    prefix="/api/leaderboard",
    tags=["leaderboard"],
)

@router.post("/submit")
async def submit_score(
    item: GameSessionCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    try:
        # Start transaction (handled by session context manager or implicit commit)
        # 1. Insert Game Session
        new_session = GameSession(user_id=item.user_id, score=item.score, game_mode=item.game_mode)
        db.add(new_session)
        
        # 2. Update Leaderboard Table (Atomic increment/Insert)
        # Check if entry exists
        # This part should be atomic. We can use ON CONFLICT/UPSERT logic or simple check-update in transaction
        # For simplicity and speed in this demo, we'll try to get and update.
        # Ideally, we'd use raw SQL or SQLAlchemy specialized constructs for atomicity.
        
        # Using raw SQL for efficient UPSERT (PostgreSQL specific)
        stmt = text("""
            INSERT INTO leaderboard (user_id, total_score, rank)
            VALUES (:uid, :score, 0)
            ON CONFLICT (user_id) 
            DO UPDATE SET total_score = leaderboard.total_score + EXCLUDED.total_score
        """)
        await db.execute(stmt, {"uid": item.user_id, "score": item.score})
        await db.commit()

        # 3. Update Redis (Write-through/Write-back)
        # ZINCRBY: Increment the score of the member in the sorted set
        await redis.zincrby("leaderboard_scores", item.score, str(item.user_id))
        
        return {"message": "Score submitted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top", response_model=LeaderboardResponse)
async def get_top_users(redis: Redis = Depends(get_redis), db: Session = Depends(get_db)):
    # Try getting from Redis
    top_users_raw = await redis.zrevrange("leaderboard_scores", 0, 9, withscores=True)
    
    if top_users_raw:
        # Format response
        result = []
        for i, (uid, score) in enumerate(top_users_raw):
            result.append({"user_id": int(uid), "total_score": int(score), "rank": i + 1})
        return {"top_players": result}
    
    # Fallback to DB if Redis is empty
    top_entries = await db.execute(text("SELECT user_id, total_score FROM leaderboard ORDER BY total_score DESC LIMIT 10"))
    result = []
    for i, row in enumerate(top_entries):
        # Populate Redis for next time
        await redis.zadd("leaderboard_scores", {str(row.user_id): row.total_score})
        result.append({"user_id": row.user_id, "total_score": row.total_score, "rank": i + 1})
        
    return {"top_players": result}

@router.get("/rank/{user_id}", response_model=UserRank)
async def get_user_rank(user_id: int, redis: Redis = Depends(get_redis), db: Session = Depends(get_db)):
    # Try Redis
    rank = await redis.zrevrank("leaderboard_scores", str(user_id))
    score = await redis.zscore("leaderboard_scores", str(user_id))
    
    if rank is not None and score is not None:
        return {"user_id": user_id, "rank": rank + 1, "total_score": int(score)}
        
    # Fallback to DB
    # Calculate rank via DB (expensive)
    result = await db.execute(text("""
        SELECT total_score, 
        (SELECT COUNT(*) + 1 FROM leaderboard l2 WHERE l2.total_score > l1.total_score) as rank
        FROM leaderboard l1
        WHERE user_id = :uid
    """), {"uid": user_id})
    
    row = result.first()
    if not row:
         raise HTTPException(status_code=404, detail="User not found")
         
    # Update Redis
    await redis.zadd("leaderboard_scores", {str(user_id): row.total_score})
    
    return {"user_id": user_id, "rank": row.rank, "total_score": row.total_score}
