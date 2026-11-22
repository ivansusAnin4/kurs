
from fastapi import APIRouter, Request, Form, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import ValidationError
from schemas import FeedbackCreate, SearchParams
from fastapi import Body
from schemas import UserCreate, UserResponse
import datetime
from dependencies import get_current_user, get_pagination_params

router = APIRouter(
    prefix="",
    tags=["Pages"],
    responses={404: {"description": "Страница не найдена"}}
)

templates = Jinja2Templates(directory="templates")


@router.post("/feedback", response_class=HTMLResponse)
async def submit_feedback(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    rating: int = Form(...)
):
    """Обработка POST-запроса с валидацией через Pydantic"""
    
    errors = []
    

    try:
        feedback_data = FeedbackCreate(
            name=name,
            email=email,
            message=message,
            rating=rating
        )
        
        return templates.TemplateResponse(
            "feedback_success.html",
            {
                "request": request,
                "name": feedback_data.name,
                "email": feedback_data.email,
                "message": feedback_data.message,
                "rating": feedback_data.rating
            }
        )
    
    except ValidationError as e:
        # Собираем все ошибки валидации
        for error in e.errors():
            errors.append(f"{error['loc'][0]}: {error['msg']}")
        
        # Возвращаем форму с ошибками
        return templates.TemplateResponse(
            "feedback.html",
            {
                "request": request,
                "errors": errors,
                "form_data": {"name": name, "email": email, "message": message, "rating": rating}
            }
        )


@router.get("/search", response_class=HTMLResponse)
async def advanced_search(
    request: Request,
    q: Optional[str] = Query(None, max_length=100, description="Поисковый запрос"),
    category: Optional[str] = Query("all", pattern="^(all|electronics|books|clothing)$", description="Категория"),
    min_price: Optional[int] = Query(None, ge=0, description="Мин. цена"),
    max_price: Optional[int] = Query(None, ge=0, description="Макс. цена"),
    sort_by: str = Query("name", pattern="^(name|price)$", description="Сортировка"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Порядок"),
    page: int = Query(1, ge=1, description="Страница"),
    limit: int = Query(10, ge=1, le=50, description="Записей на странице")
):
    """Расширенный поиск с валидацией всех параметров через Query"""
    
    # Валидация через Pydantic модель
    try:
        params = SearchParams(
            q=q, category=category, min_price=min_price,
            max_price=max_price, sort_by=sort_by, order=order,
            page=page, limit=limit
        )
    except ValidationError as e:
        # Если валидация не прошла, показываем ошибку
        return templates.TemplateResponse(
            "search.html",
            {
                "request": request,
                "error": "Некорректные параметры поиска",
                "validation_errors": e.errors()
            }
        )
    
    # Тестовые данные
    all_items = [
        {"id": 1, "name": "Война и мир", "category": "books", "price": 1200},
        {"id": 2, "name": "Анна Каренина", "category": "books", "price": 600},
        {"id": 3, "name": "1984", "category": "books", "price": 700},
        {"id": 4, "name": "Мцыри", "category": "books", "price": 90},
        {"id": 5, "name": "Книга Python для начинающих", "category": "books", "price": 1500},
        {"id": 6, "name": "Книга FastAPI в действии", "category": "books", "price": 2500},
        {"id": 7, "name": "В мире науки", "category": "magazine", "price": 800},
        {"id": 8, "name": "Юный техник", "category": "magazine", "price": 350},
        {"id": 9, "name": "За рулём", "category": "magazine", "price": 150},
        {"id": 10, "name": "Книга Django для профессионалов", "category": "books", "price": 3000},
        {"id": 11, "name": "Forbes", "category": "magazine", "price": 350},
        {"id": 12, "name": "Top Gear 2006", "category": "DVD", "price": 1500},
        {"id": 13, "name": "Пакет офисных программ", "category": "DVD", "price": 3000},
        {"id": 14, "name": "Windows XP", "category": "DVD", "price": 3000},
        {"id": 15, "name": "Пакет программ Libre Office", "category": "DVD", "price": 3000},
        {"id": 16, "name": "Windows 10", "category": "DVD", "price": 3000},
    ]
    
    results = all_items.copy()
    
    # Поиск по названию
    if params.q:
        results = [item for item in results if params.q.lower() in item["name"].lower()]
    
    # Фильтрация по категории
    if params.category != "all":
        results = [item for item in results if item["category"] == params.category]
    
    # Фильтрация по цене
    if params.min_price is not None:
        results = [item for item in results if item["price"] >= params.min_price]
    if params.max_price is not None:
        results = [item for item in results if item["price"] <= params.max_price]
    
    # Сортировка
    if params.sort_by == "name":
        results.sort(key=lambda x: x["name"], reverse=(params.order == "desc"))
    elif params.sort_by == "price":
        results.sort(key=lambda x: x["price"], reverse=(params.order == "desc"))
    
    # Пагинация
    total_items = len(results)
    start = (params.page - 1) * params.limit
    end = start + params.limit
    paginated_items = results[start:end]
    total_pages = (total_items + params.limit - 1) // params.limit
    
    return templates.TemplateResponse(
        "search_advanced.html",
        {
            "request": request,
            "items": paginated_items,
            "total_items": total_items,
            "page": params.page,
            "total_pages": total_pages,
            "params": params
        }
    )
    
# API эндпоинт с валидацией (возвращает JSON)
@router.post("/api/register", response_model=UserResponse)
async def api_register(user_data: UserCreate = Body(...)):
    """Пример API эндпоинта с автоматической валидацией через Pydantic"""
    
    return UserResponse(
        id=1,
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        created_at=datetime.now(),
        is_active=True
    )
    
# Страница входа (GET)
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Страница авторизации"""
    return templates.TemplateResponse("form.html", {"request": request, "error": None})

# Обработка входа (POST)
@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Обработка формы входа с установкой cookie"""
    
    # Простая проверка
    if username == "admin" and password == "admin":
        # Создаем ответ с установкой cookie
        response = templates.TemplateResponse(
            "login_success.html",
            {"request": request, "username": username}
        )
        # Устанавливаем cookie с именем пользователя
        response.set_cookie(
            key="username", 
            value=username, 
            max_age=3600,
            path="/" 
        )
        return response
    else:
        return templates.TemplateResponse(
            "form.html",
            {"request": request, "error": "Неверное имя пользователя или пароль"}
        )
        
@router.get("/items", response_class=HTMLResponse)
async def list_items(
    request: Request, 
    pagination: dict = Depends(get_pagination_params),  # Зависимость
    category: str = "all"
):
    """Список товаров с пагинацией через зависимость"""
    
    all_items = [
        {"id": 1, "name": "Война и мир", "category": "books", "price": 1200},
        {"id": 2, "name": "Анна Каренина", "category": "books", "price": 600},
        {"id": 3, "name": "1984", "category": "books", "price": 700},
        {"id": 4, "name": "Мцыри", "category": "books", "price": 90},
        {"id": 5, "name": "Книга Python для начинающих", "category": "books", "price": 1500},
        {"id": 6, "name": "Книга FastAPI в действии", "category": "books", "price": 2500},
        {"id": 7, "name": "В мире науки", "category": "magazine", "price": 800},
        {"id": 8, "name": "Юный техник", "category": "magazine", "price": 350},
        {"id": 9, "name": "За рулём", "category": "magazine", "price": 150},
        {"id": 10, "name": "Книга Django для профессионалов", "category": "books", "price": 3000},
        {"id": 11, "name": "Forbes", "category": "magazine", "price": 350},
        {"id": 12, "name": "Top Gear 2006", "category": "DVD", "price": 1500},
        {"id": 13, "name": "Пакет офисных программ", "category": "DVD", "price": 3000},
        {"id": 14, "name": "Windows XP", "category": "DVD", "price": 3000},
        {"id": 15, "name": "Пакет программ Libre Office", "category": "DVD", "price": 3000},
        {"id": 16, "name": "Windows 10", "category": "DVD", "price": 3000},
    ]
    
    # Фильтрация по категории
    if category != "all":
        items = [item for item in all_items if item["category"] == category]
    else:
        items = all_items
    
    # Используем параметры пагинации из зависимости
    total_items = len(items)
    start = pagination["offset"]
    end = start + pagination["limit"]
    paginated_items = items[start:end]
    
    total_pages = (total_items + pagination["limit"] - 1) // pagination["limit"] if total_items > 0 else 1
    
    return templates.TemplateResponse(
        "items.html",
        {
            "request": request,
            "items": paginated_items,
            "page": pagination["page"],
            "limit": pagination["limit"],
            "category": category,
            "total_items": total_items,
            "total_pages": total_pages
        }
    )


@router.get("/profile", response_class=HTMLResponse)
async def user_profile(
    request: Request, 
    current_user: dict = Depends(get_current_user)  
):
    """Профиль текущего пользователя"""
    if not current_user.get("authenticated"):
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request, 
            "user": current_user
        }
    )
    
