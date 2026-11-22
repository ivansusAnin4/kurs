from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from dependencies import require_admin

router = APIRouter(
    prefix="/admin",  # Префикс для всех админских маршрутов
    tags=["Admin"],   # Тег для группировки в документации
    responses={404: {"description": "Админ-панель: страница не найдена"}}
)

templates = Jinja2Templates(directory="templates")

users_db = {
    "alex": {"name": "Алексей", "email": "alex@example.com", "role": "admin", "active": True},
    "maria": {"name": "Мария", "email": "maria@example.com", "role": "user", "active": True},
    "ivan": {"name": "Иван", "email": "ivan@example.com", "role": "user", "active": False}
}

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request, 
    admin_user: dict = Depends(require_admin)  
):
    """Главная админ-панели (только для админов)"""
    stats = {
        "total_users": len(users_db),
        "active_users": sum(1 for u in users_db.values() if u["active"]),
        "admin_count": sum(1 for u in users_db.values() if u["role"] == "admin")
    }
    return templates.TemplateResponse(
        "admin/dashboard.html", 
        {"request": request, "stats": stats, "admin_user": admin_user}
    )

@router.get("/users", response_class=HTMLResponse)
async def admin_users(
    request: Request, 
    admin_user: dict = Depends(require_admin)  
):
    """Управление пользователями (только для админов)"""
    return templates.TemplateResponse(
        "admin/users.html", 
        {"request": request, "users": users_db, "admin_user": admin_user}
    )

@router.get("/users/{username}", response_class=HTMLResponse)
async def admin_user_detail(request: Request, username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    return templates.TemplateResponse(
        "admin/user_detail.html",
        {"request": request, "username": username, "user": users_db[username]}
    )

@router.post("/users/{username}/toggle")
async def toggle_user_status(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    users_db[username]["active"] = not users_db[username]["active"]
    return RedirectResponse(url="/admin/users", status_code=303)

@router.post("/users/{username}/delete")
async def delete_user(username: str):
    if username not in users_db:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    if users_db[username]["role"] == "admin":
        raise HTTPException(status_code=403, detail="Нельзя удалить администратора")
    
    del users_db[username]
    return RedirectResponse(url="/admin/users", status_code=303)

@router.get("/", response_class=HTMLResponse)
async def admin_root():
    return RedirectResponse(url="/admin/dashboard")


@router.get("/my-profile", response_class=HTMLResponse)
async def my_profile(request: Request):
    """Профиль пользователя (временное решение)"""
    username = request.cookies.get("username", "guest")
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": {"username": username, "role": "user", "authenticated": username != "guest"}}
    )