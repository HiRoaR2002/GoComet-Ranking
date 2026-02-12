from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from .routers import leaderboard
from .database import engine, Base
import os
import time
import newrelic.agent

# Initialize New Relic with configuration file
NEW_RELIC_LICENSE_KEY = os.getenv("NEW_RELIC_LICENSE_KEY")
if NEW_RELIC_LICENSE_KEY:
    try:
        # Set environment variable for config file
        os.environ["NEW_RELIC_LICENSE_KEY"] = NEW_RELIC_LICENSE_KEY
        
        # Initialize with config file
        config_file = os.path.join(os.path.dirname(__file__), "..", "newrelic.ini")
        if os.path.exists(config_file):
            newrelic.agent.initialize(config_file)
            print(f"✅ New Relic agent initialized with config file: {config_file}")
        else:
            # Fallback to programmatic initialization
            newrelic.agent.initialize()
            print("✅ New Relic agent initialized (no config file)")
    except Exception as e:
        print(f"❌ Failed to initialize New Relic: {e}")

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

# Custom middleware for New Relic metrics
@app.middleware("http")
async def new_relic_metrics_middleware(request: Request, call_next):
    """Track custom metrics for each request"""
    start_time = time.time()
    
    # Add custom attributes to the transaction
    if NEW_RELIC_LICENSE_KEY:
        transaction = newrelic.agent.current_transaction()
        if transaction:
            # Add custom parameters to track
            transaction.add_custom_attribute('request_path', request.url.path)
            transaction.add_custom_attribute('request_method', request.method)
            transaction.add_custom_attribute('client_host', request.client.host if request.client else 'unknown')
    
    # Process the request
    response = await call_next(request)
    
    # Calculate response time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Record custom metrics in New Relic
    if NEW_RELIC_LICENSE_KEY:
        try:
            # Record response time metric
            newrelic.agent.record_custom_metric(f'Custom/ResponseTime/{request.url.path}', process_time)
            
            # Record status code metric
            newrelic.agent.record_custom_metric(f'Custom/StatusCode/{response.status_code}', 1)
            
            # Record endpoint-specific metrics
            if request.url.path.startswith('/api/leaderboard'):
                endpoint_name = request.url.path.split('/')[-1] or 'root'
                newrelic.agent.record_custom_metric(f'Custom/Leaderboard/{endpoint_name}/ResponseTime', process_time)
                newrelic.agent.record_custom_metric(f'Custom/Leaderboard/{endpoint_name}/Calls', 1)
        except Exception as e:
            print(f"Failed to record New Relic metric: {e}")
    
    return response


# Startup
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(leaderboard.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
