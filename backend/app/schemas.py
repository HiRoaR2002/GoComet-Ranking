from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str

class GameSessionCreate(BaseModel):
    user_id: int
    score: int
    game_mode: str = "default"

class LeaderboardEntry(BaseModel):
    user_id: int
    total_score: int
    rank: int

    class Config:
        orm_mode = True

class UserRank(BaseModel):
    user_id: int
    rank: int
    total_score: int

class LeaderboardResponse(BaseModel):
    top_players: list[LeaderboardEntry]
