# импорт модулей
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update                    
import requests
import aiohttp
from telegram.constants import MessageLimit
# from dotenv import load_dotenv
# load_dotenv("../.env")

# токен бота напрямую в коде
TOKEN = "7659555766:AAHeC81MyIRCz_onUkTdZJhfdyS9tGxgg7A"

# функция-обработчик команды /start
async def start(update, context):

    # сообщение пользователю
    await update.message.reply_text("Привет! Я консультант онлайн-школы Sirius Future!")

# функция-обработчик текстовых сообщений

# async def text(update, context):

#     # обращение к API база Sirius Future
#     param = {
#         'text': update.message.text
#     }    
#     async with aiohttp.ClientSession() as session:
#         async with session.post('http://127.0.0.1:8000/api/get_answer_async', json = param) as response:

#             # получение ответа от API
#             answer = await response.json()

#             # ответ пользователю
#             await update.message.reply_text(answer['message'])   
            
                  
async def text(update, context):
    param = {
        'user_id': update.message.from_user.id,
        'text': update.message.text
    }

    async with aiohttp.ClientSession() as session:
        async with session.post('http://127.0.0.1:8000/api/get_answer_async', json=param) as response:
            if response.status == 200:
                data = await response.json()
                answer = data['message']
               # chunks = data['chunks']

                # Отправляем ответ пользователю
                await update.message.reply_text(answer)

                # # Отправляем чанки отдельным сообщением (опционально)
                # if len(chunks) > MessageLimit.MAX_TEXT_LENGTH:
                #     # разбиваем текст на части до 4000 символов
                #     for i in range(0, len(chunks), 4000):
                #         await update.message.reply_text(chunks[i:i+4000])
                # else:
                #     await update.message.reply_text(f"📄 Релевантные чанки:\n{chunks}")
            else:
                error_msg = await response.text()
                await update.message.reply_text(f"Ошибка API: {error_msg}")


# функция "Запуск бота"
def main():

    # создаем приложение и передаем в него токен
    application = Application.builder().token(TOKEN).connect_timeout(20).build()

    # добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # добавляем обработчик текстовых сообщений
    application.add_handler(MessageHandler(filters.TEXT, text))

    # запускаем бота (нажать Ctrl-C для остановки бота)
    print('Бот запущен...')    
    application.run_polling()
    print('Бот остановлен')

# проверяем режим запуска модуля
if __name__ == "__main__":
    main()
