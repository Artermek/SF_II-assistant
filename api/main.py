from fastapi import FastAPI                         # библиотека FastAPI
from pydantic import BaseModel                      # модуль для объявления структуры данных
from api.chunks import Chunk                        # модуль для работы с OpenAI
from fastapi.middleware.cors import CORSMiddleware  # класс для работы с CORS
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException
from fastapi import HTTPException
from openai import AsyncOpenAI
import os
# создаем объект приложения FastAPI
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# создадим объект для работы с OpenAI
chunk = Chunk()

# класс с типами данных для метода api/get_answer
class ModelAnswer(BaseModel):
    user_id: int
    text: str   
    
# класс параметров запроса к openai
class ModelRequest(BaseModel):
    system: str = ''
    user: str = ''
    temperature: float = 0.2
    format: dict = None

# функция, которая будет обрабатывать запрос по пути "/"
# полный путь запроса http://127.0.0.1:8000/
@app.get("/")
def root(): 
    return {"message": "Hello FastAPI !!!"}

# функция, которая обрабатывает запрос по пути "/about"
@app.get("/about")
def about():
    return {"message": "Страница с описанием проекта"}

# функция-обработчик с параметрами пути
@app.get("/users/{id}")
def users(id):
    return {"Вы ввели user_id": id}  


# функция обработки post запроса + декоратор  (асинхронная)
@app.post('/api/get_answer_async')
async def get_answer_async(question: ModelAnswer):
    result = await chunk.get_answer_async(user_id=question.user_id, query=question.text, verbose=True)
    return {
        'message': result["answer"], 
        'chunks': result["chunks"]
    }

# функция обращения к openai
@app.post('/api/request')
async def post_request(question: ModelRequest):
    answer = await chunk.request(
        system = question.system,
        user = question.user,
        temp = question.temperature,
        format = question.format
    )
    return {'message': answer} 

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": f"Ошибка сервера: {str(exc)}"},
    )
    
    
    
@app.get("/api/check_openai_key")
async def check_openai_key():
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY не задан!")

    client = AsyncOpenAI(api_key=api_key)
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'API is working!'."}
            ],
            max_tokens=10
        )
        if response.choices:
            return {"success": True, "message": response.choices[0].message.content}
        else:
            return {"success": False, "message": "No response from OpenAI API."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {str(e)}")