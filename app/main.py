from fastapi import FastAPI
from app.api.users import router as users_router
from app.db.session import init_db
from app.services.middleware import log_requests  
from app.services.logs import start_log_rotation 

# Initialize the FastAPI app
app = FastAPI()

@app.get("/health")
async def health_check():
    # You can add more logic here, like database checks, etc.
    return {"status": "OK"}

# Initialize the database
@app.on_event("startup")
def on_startup():
    init_db()
    start_log_rotation()  # Start log rotation scheduler

# Include the users router
app.include_router(users_router, prefix="/api")

# Add the middleware to the FastAPI app
app.middleware("http")(log_requests)  # Register the log_requests middleware

