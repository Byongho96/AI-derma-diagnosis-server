from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import validation_exception_handler
from app.models.base import Base

from app.api.v1 import diagnoses, users
from app.db.session import engine

'''
Create all database tables.
- The database specified in DATABASE_URL must exist.
- All database models MUST BE IMPORTED before this line to ensure they are registered in the metadata.
- CREATE TABLE IF NOT EXISTS is not used, so existing tables are not affected.
'''
Base.metadata.create_all(bind=engine)


'''
Create FastAPI app instance and include routers.
'''
app = FastAPI()

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

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(diagnoses.router, prefix="/api/v1/diagnoses", tags=["diagnoses"])

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the API"}