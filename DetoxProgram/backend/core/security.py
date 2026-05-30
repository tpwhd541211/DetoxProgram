import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings

security_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    """
    FastAPI dependency to extract and verify the Supabase access token (JWT).
    Returns the user's UUID if valid, raising a 401 error otherwise.
    """
    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token is missing"
        )
        
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": settings.SUPABASE_ANON_KEY
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{settings.SUPABASE_URL}/auth/v1/user",
                headers=headers,
                timeout=5.0
            )
            
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token"
            )
            
        user_info = resp.json()
        user_id = user_info.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        return user_id
    except httpx.RequestError as exc:
        print(f"Network error verifying token: {exc}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to reach authentication server"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Auth token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )
