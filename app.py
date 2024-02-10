# FastAPI

from fastapi import FastAPI, File, UploadFile, Request  # APIRouter - здесь не нужен, все добавляем напрямую к app
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
import tempfile
from datetime import datetime
from pilot_model import pilot_model
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# Создание объекта FastAPI, который отвечает за обработку запросов и маршрутизацию
app = FastAPI(title="Segmentation_API", version="0.1.0", debug=True)

# добавляет новый роутер, который определяет новый набор эндпоинтов для API
#router = APIRouter()
#app.include_router(router)

# Разрешаем CORS для всех доменов
# CORS Middleware (Cross-Origin Resource Sharing) для обеспечения безопасного обмена данными
# между сервером и клиентами (веб-приложение, android-приложение),
# для разрешения кросс-доменных запросов от любого домена и настройки заголовков безопасности
#origins = ["*"]
origins = [
    "http://localhost:3000",
    "http://51.250.26.141",
    "http://195.91.179.130:3000",
]

# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
#    allow_origins=origins,
    allow_credentials=True,
#    allow_methods=["*"],
#    allow_headers=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # перечислите допустимые методы
    allow_headers=["Content-Type", "Authorization"],  # перечислите допустимые заголовки
)


app.add_middleware(
    GZipMiddleware,
    minimum_size=1000, # сжимать только ответы размером больше 1000 байт
)


# Добавляем middleware для CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Добавление статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/info")
def read_root():
    return {"Project 2023. Yandex Cloud": "Tree_Segmentation"}


@app.get("/date")
async def get_current_date():
    return {"date": datetime.now().date()}


@app.get("/power")
def power(x: int=25, y: int=2):
    return [x, y, x**y]


# Обработка изображения
@app.post("/process_image")
async def process_image(image: UploadFile = File(...)):
    # Загрузка изображения из запроса
    image_data = await image.read()
    pil_image = Image.open(BytesIO(image_data))

    # Обработка изображения с помощью функции pilot_model
    result = pilot_model(pil_image)

    # Сохранение результата во временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
        cv2.imwrite(temp_file.name, result)

        # Отправка результата обратно клиенту
        return FileResponse(temp_file.name, media_type="image/png", headers={"Content-Disposition": f"attachment; filename={image.filename}_processed.png"})
