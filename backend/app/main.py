from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import leaderboard
from .database import engine, Base
import os
import newrelic.agent

# Initialize New Relic if license key is present
if os.getenv("NEW_RELIC_LICENSE_KEY"):
    try:
        newrelic.agent.initialize(config_file=None, environment=None)
        print("New Relic agent initialized.")
    except Exception as e:
        print(f"Failed to initialize New Relic: {e}")

app = FastAPI(
    title="Gaming Leaderboard",
    description="API for submitting scores and retrieving leaderboard stats.",
    version="1.0.0",
)

# CORS
origins = [
    "http://localhost:3000",
    "http://localhost:5173", # Vite
    "http://127.0.0.1:5173",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(leaderboard.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
