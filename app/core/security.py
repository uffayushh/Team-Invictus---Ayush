import jwt
from fastapi import Header, HTTPException

from app.core.config import settings


def get_current_user_id(authorization: str = Header(...)) -> str:
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"error": {
            "code": "missing_token", "message": "Missing or malformed Authorization header."}})

    token = authorization.removeprefix("Bearer ").strip()

    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail={"error": {
            "code": "token_expired", "message": "Session expired, please log in again."}})
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail={"error": {
            "code": "invalid_token", "message": f"Invalid token: {e}"}})

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail={"error": {
            "code": "invalid_token", "message": "Token missing subject claim."}})

    return user_id