from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1 import diagnoses, users
from app.core.exceptions import validation_exception_handler
from app.db.session import engine
from app.models.base import Base

'''
Create all database tables.
- The database specified in DATABASE_URL must exist.
- All database models MUST BE IMPORTED before this line to ensure they are registered in the metadata.
- CREATE TABLE IF NOT EXISTS is not used, so existing tables are not affected.
'''
Base.metadata.create_all(bind=engine)


# Initialize FastAPI application
app = FastAPI()

# CORS middleware configuration
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,      
    allow_methods=["*"],        
    allow_headers=["*"],          
)

# static files configuration
static_dir_path = str(settings.STATIC_DIR.resolve())

# Ensure the static directory exists
Path(static_dir_path).mkdir(parents=True, exist_ok=True) 

app.mount(
    settings.STATIC_URL_PREFIX,
    StaticFiles(directory=static_dir_path),
    name="static-images"
)

# Register exception handlers and API routers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(diagnoses.router, prefix="/api/v1/diagnoses", tags=["diagnoses"])

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}