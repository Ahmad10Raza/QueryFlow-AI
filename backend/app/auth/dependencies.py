from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.services.user_mongodb import UserMongoService
from app.models.user_mongo import UserDocument

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserDocument:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print(f"DEBUG AUTH: Token received: {token[:10]}..." if token else "DEBUG AUTH: No token")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        print(f"DEBUG AUTH: Decoded email: {email}")
        if email is None:
            print("DEBUG AUTH: Email is None")
            raise credentials_exception
    except JWTError as e:
        print(f"DEBUG AUTH: JWTError: {e}")
        raise credentials_exception
    
    user = await UserMongoService.get_user_by_email(email)
    if user is None:
        print(f"DEBUG AUTH: User not found for email: {email}")
        raise credentials_exception
    return user

async def require_super_admin(current_user: UserDocument = Depends(get_current_user)):
    if not current_user.role_name or current_user.role_name != "SUPER_ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Super Admin access required."
        )
    return current_user

async def require_admin(current_user: UserDocument = Depends(get_current_user)):
    if not current_user.role_name or current_user.role_name not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user
