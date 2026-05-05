"""
File: backend/app/routers/auth.py
Description: Authentication and authorization endpoints.
TODO:
- Implement register logic (hash password, save user).
- Implement login logic (verify password, generate JWT token).
- Implement change password logic.
- Add Pydantic schemas for request/response.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register():
    """Register a new user."""
    raise NotImplementedError("Registration not implemented yet")

@router.post("/login")
async def login():
    """Authenticate user and return token."""
    raise NotImplementedError("Login not implemented yet")

@router.post("/change-password")
async def change_password():
    """Change user password."""
    raise NotImplementedError("Change password not implemented yet")
