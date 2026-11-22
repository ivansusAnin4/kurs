# dependencies/__init__.py
from fastapi import Request, HTTPException, Depends

def get_current_user(request: Request):
    """Зависимость для получения текущего пользователя из cookie"""
    username = request.cookies.get("username")
    
    if not username:
        return {"username": "guest", "role": "guest", "authenticated": False}
    
    users_db = {
        "admin": {"username": "admin", "role": "admin", "authenticated": True},
        "alex": {"username": "alex", "role": "user", "authenticated": True},
        "maria": {"username": "maria", "role": "user", "authenticated": True},
    }
    
    return users_db.get(username, {"username": "guest", "role": "guest", "authenticated": False})

def require_admin(current_user: dict = Depends(get_current_user)):
    """Зависимость, требующая права администратора"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Требуются права администратора")
    return current_user

def get_pagination_params(page: int = 1, limit: int = 10):
    """Зависимость для получения параметров пагинации"""
    return {"page": page, "limit": limit, "offset": (page - 1) * limit}