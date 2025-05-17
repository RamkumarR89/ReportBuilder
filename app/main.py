from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.core.database import get_db, engine
from app.models import models

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dynamic Reports API",
    description="API for managing dynamic reports and charts",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static", html=True), name="static")

# Root endpoint
@app.get("/api")
async def root():
    return {"message": "Welcome to Dynamic Reports API"}

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

# Only import and include the reports router
from app.api.v1 import reports
from app.api.v1 import users

app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"]) 