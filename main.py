from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import pages, admin  

app = FastAPI(
    title="Мой Первый Сайт на FastAPI", 
    description="Изучаем Full-Stack разработку с FastAPI", 
    version="1.0.0"
) 

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)  
app.include_router(admin.router)  

@app.get("/health")
async def health_check():
    return {"status": "OK", "message": "Сервер работает нормально"}

@app.exception_handler(404)
async def not_found(request, exc):
    from fastapi.responses import HTMLResponse
    return HTMLResponse("""
    <h1>404 - Страница не найдена</h1>
    <p>Извините, запрошенная страница не существует.</p>
    <a href="/">Вернуться на главную</a>
    """, status_code=404)
    
