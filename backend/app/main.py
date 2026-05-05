"""
File: backend/app/main.py
Description: FastAPI main application entry point.
TODO:
- Initialize FastAPI app.
- Configure CORS.
- Include routers (auth, admin, customer).
- Add database initialization/connection logic.
- Add exception handlers.
"""

from fastapi import FastAPI

app = FastAPI(title="X.509 Certificate Management System")

# TODO: Include routers here
# app.include_router(auth.router)
# app.include_router(admin.router)
# app.include_router(customer.router)

@app.get("/")
async def root():
    return {"message": "Welcome to X.509 Certificate Management System API"}
