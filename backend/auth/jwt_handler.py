# backend/auth/jwt_handler.py
import os
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.environ.get("DOCUMIND_SECRET", "documind-dev-secret-change-in-prod")
ALGORITHM  = "HS256"
EXPIRE_HOURS = 24 * 7   # 7 days

_bearer = HTTPBearer(auto_error=True)


def create_token(user_id: int, username: str) -> str:
    payload = {
        "sub":      str(user_id),
        "username": username,
        "exp":      datetime.now(timezone.utc) + timedelta(hours=EXPIRE_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")


def get_current_user(creds: HTTPAuthorizationCredentials = Security(_bearer)) -> dict:
    """FastAPI dependency — returns {"user_id": int, "username": str}."""
    payload = _decode(creds.credentials)
    return {"user_id": int(payload["sub"]), "username": payload["username"]}
