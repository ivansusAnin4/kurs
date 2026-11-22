# schemas/__init__.py
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator
from typing import Optional
from datetime import datetime

# Модель для пользователя
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email адрес")
    password: str = Field(..., min_length=6, description="Пароль (мин. 6 символов)")
    full_name: Optional[str] = Field(None, max_length=100)
    
    # 2. Заменяем @validator на @field_validator
    @field_validator('username')
    @classmethod  # 3. ВАЖНО: Добавляем @classmethod для V2
    def username_alphanumeric(cls, v: str) -> str:  # 4. Добавляем аннотации типов (рекомендуется)
        if not v.isalnum():
            raise ValueError('Имя пользователя должно содержать только буквы и цифры')
        return v
    
    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        return v

# Модель для отзыва
class FeedbackCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Имя отправителя")
    email: EmailStr = Field(..., description="Email для ответа")
    message: str = Field(..., min_length=10, max_length=1000, description="Сообщение")
    rating: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")
    
    @field_validator('message')
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Сообщение не может быть пустым')
        return v

# Модель для поиска и фильтрации
class SearchParams(BaseModel):
    q: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field(None, pattern="^(all|electronics|books|clothing)$")
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    sort_by: str = Field("name", pattern="^(name|price)$")
    order: str = Field("asc", pattern="^(asc|desc)$")
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    
    # 5. Валидация, зависящая от нескольких полей (@model_validator в V2)
    @model_validator(mode='after')  
    def validate_price_range(self) -> 'SearchParams':
        if self.min_price is not None and self.max_price is not None:
            if self.max_price < self.min_price:
                raise ValueError('Максимальная цена не может быть меньше минимальной')
        return self

# Модель для ответа
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True  #