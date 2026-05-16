# File: middleware/auth.py
from fastapi import Request, HTTPException
from supabase import create_client

async def get_current_user(request: Request):
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    # Logic to verify Supabase JWT
    return {"id": "user_123", "role": "authenticated"}
