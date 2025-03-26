
import os
import openai
from fastapi import HTTPException, status
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.docstore.document import Document
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains import ConversationalRetrievalChain

class Chunk():
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise HTTPException(status_code=500, detail="OPENAI_API_KEY не указан в переменных окружения")

        # Передаём ключ в официальный openai
        openai.api_key = self.api_key

        self.base_load()
        self.user_memory = {}

        # Системное сообщение
        self.system = """
        ... (ваш большой текст про роли, правила, курсы и т.д.) ...
        """

    def base_load(self):
        with open('api/base/SF.txt', 'r', encoding='utf-8') as file:
            document = file.read()

        headers_to_split_on = [
            ("##", "header")
        ]
        splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        chunks = splitter.split_text(document)
        source_chunks = [Document(page_content=chunk.page_content, metadata=chunk.metadata) for chunk in chunks]

        embeddings = OpenAIEmbeddings()  # из langchain_openai
        self.db = FAISS.from_documents(source_chunks, embeddings)
# Введи проактивную бессеу, спрашивай у клиента что его интересует. 
        self.system = '''
            Ты-консультант в онлайн школе для детей Sirius Future ответь на вопрос клиента на основе документа с информацией.
            Твоя задачи: записать клиента на пробный урок, или рассказать о стоимости курса и предложить клиенту записать его на
            пробный урок, или ответить на интересующие его вопросы
            Если он 
            Не придумывай ничего от себя, отвечай максимально по документу.
            Не упоминай Документ с информацией для ответа клиенту.
            Клиент ничего не должен знать про Документ с информацией для ответа клиенту  
            Отвечай без маркдаун разметки 
            
            
            информация о курсах в онлайн школе: 
            1. Ментальная арифметика (4-14 лет): развитие интеллекта через счёт на абакусе, переход к устному счёту, мелкая моторика, память, внимание, логика; 
            4 уровня сложности; средняя длительность уровня — 2-4 месяца; доступна на английском и немецком языках; есть олимпиады.
            2. Математика 1-4 класс: индивидуальный разбор школьной программы (1-4 кл.), устранение пробелов, интерактивные задания, нет домашних заданий; 
            сюжетный подход в 1 классе.
            3. Основы арифметики (3+ лет): счёт от 0 до 10, простые задачи на сложение и вычитание, развитие логики, внимания и памяти, подготовка к ментальной 
            арифметике; 30 уроков; рекомендована планшетная форма обучения; доступна на английском и немецком языках.
            4. Чтение (4-10 лет): обучение чтению с нуля за 4 месяца; развитие речи, дикции, памяти, моторики и восприятия; постепенное усложнение от звуков 
            до предложений и текста; 12-45 уроков.
            5. Скорочтение (6-14 лет): увеличение скорости чтения, развитие памяти, внимания, навыков анализа текста, дикции; четыре уровня сложности, 
            результаты после первого уровня (30-40 уроков на уровень).
            6. Таблица умножения: изучение таблицы умножения до 10, методы запоминания, игровая форма обучения, доступен сокращенный курс за 12 уроков или 
            полный за 24 урока.
            Подготовка к школе (5-7 лет): основы чтения, письма, окружающий мир, логика, мышление, мелкая моторика; психологическая и интеллектуальная 
            подготовка к школе за 24 урока.
            
                 Программирование (Скретч Джуниор, Скретч, Роблокс 5-17 лет): 
            7. Scratch Junior (4-7 лет): блочное программирование для детей без навыков чтения, создание анимаций и 2D-игр, 30 уроков.
            8. Scratch (6-12 лет): создание игр и мультфильмов, развитие логического и алгоритмического мышления, 24 урока.
            9.Roblox (9-14 лет): 3D-моделирование и программирование на Lua, создание игр, 24 урока, требует знания английского и базовых навыков 
            программирования.
            8. Английский язык Vocaboo (4-12 лет): разговорный английский с элементами Phonics, проектная деятельность, уровни от А0 до А2, занятия 25-45 
            минут; отдельный интенсив для детей 9-12 лет.
            Русский как иностранный для детей (6-14 лет): комплексное изучение русского языка (говорение, письмо, чтение, культура), два уровня А2 и B1 по 
            32 урока.
            9. ТРИЗ-Мастермайнд (5-13 лет): развитие творческого и инженерного мышления, навыков решения нестандартных задач, работа в группе, 48 уроков в 
            годовом курсе.
            10. Кубик Рубика: Обучим вашего ребенка собирать кубик рубик. Мы покажем два разных способа сборки.
            
            
            не путай цены на обычные услуги и на диагностику
            Если вопрос от пользователя связан с трудоустройством, поиском работы и с тем, есть ли вакантные места, то на этот вопрос
            отправляй примерно следующие сообщение "https://siriusfuture.ru/teacher вся информация для учителей. Изучите информацию 
            на сайте, заполните форму и с Вами обязательно свяжутся"   
            Если в документах нету информации по вопросу пользователя, то не придумывай ничего от себя и ответь что не знаешь
            
            Если вопрос пользователя связан с тем, что он не может зайти на урок, что у него не работает платформа, а так же все остальное, связанное
            с технической частью, то отправляй примерно следующие сообщение 'Напишите пожалуйста в WhatsAPP нашим администраторам, они вам 
            помогут +7 (958) 500-90-22'  
            
            Если это 1 неразборчивое сообщение, уточни запрос пользователя.
            Если клиент спамит, пишет неразборчиво много разных симболов, отправляет несвязанные слова в 2 или более сообщениях подряд (отслеживай это по 
            истории сообщений), то это пишет ребенок и твоя задача позвать его играть на сайт https://siriusfuture.ru/simulators/number-composition 
            это игра про состав чисел.'Двигайся от вершины к основанию, заполняя числа. Помни что верхнее число — это сумма двух нижних чисел под ним.'
        '''


    async def request(self, system, user, model='gpt-4o-mini', temp=None, format: dict=None):

        messages = [
            {'role': 'system', 'content': system},
            {'role': 'user', 'content': user}
        ]

        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=messages,
                temperature=temp,
                response_format=format
            )

            if response.choices:
                return response.choices[0].message.content
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail='Не удалось получить ответ от модели.')
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail=f'Ошибка при запросе в OpenAI: {e}')

    async def get_answer_async(self, user_id: int, query: str, verbose=True):
        # Если память для пользователя ещё не создана — создаём
        if user_id not in self.user_memory:
            # Обычно memory не требует параметра llm=, можно убрать
            self.user_memory[user_id] = ConversationBufferWindowMemory(k=3)

        # Вытаскиваем историю
        history = self.user_memory[user_id].load_memory_variables({})
        if isinstance(history['history'], str):
            conversation_history = history['history']
        else:
            # Если в history['history'] массив сообщений, соберём их
            conversation_history = "\n".join(msg.content for msg in history['history'])

        # Ищем похожие куски в FAISS
        docs = self.db.similarity_search(query, k=3)
        message_content = '\n'.join([doc.page_content for doc in docs])

        if verbose:
            print('-----------------------------------------------')
            print('Релевантные чанки:\n', message_content)
            print('-----------------------------------------------')
            print('История диалога:\n', conversation_history)

        # Формируем prompt c учётом найденных чанков
        user_prompt = f"""
            Ты онлайн-консультант в детской онлайн-школе.
            Ответь на вопрос клиента. Не упоминай документ с информацией для ответа клиенту в ответе.
            Документ с информацией для ответа клиенту: {message_content}

            История разговора:
            {conversation_history}

            Вопрос клиента:
            {query}
        """

        # Отправляем на модель
        answer = await self.request(self.system, user_prompt, model='gpt-4o-mini', temp=0)

        # Сохраняем новый кусок диалога в память
        self.user_memory[user_id].save_context({"input": query}, {"output": answer})

        return {"answer": answer, "chunks": message_content}