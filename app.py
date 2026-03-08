import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="StudyFlow AI", layout="wide")

st.title("🎓 StudyFlow: Твой AI-помощник в учебе")
st.write("Загрузи фото конспекта или просто задай тему, а я сделаю тесты и выжимку.")

# --- ПОДКЛЮЧЕНИЕ К GEMINI ---
# Мы берем ключ из секретов хостинга (об этом ниже)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3.0-flash') # Быстрая и бесплатная модель
except Exception as e:
    st.error("Ошибка ключа API. Укажите его в настройках Streamlit Cloud.")

# --- ИНТЕРФЕЙС ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Загрузка материала")
    uploaded_file = st.file_uploader("Фото конспекта (JPG, PNG)", type=["jpg", "png"])
    
    user_question = st.text_area("Или просто напиши тему/вопрос здесь:")

    generate_btn = st.button("🚀 Разобрать материал")

with col2:
    st.header("2. Результат")
    
    if generate_btn:
        prompt = ""
        content = []

        # Формируем запрос к нейросети
        base_prompt = """
        Ты опытный преподаватель. Проанализируй этот материал.
        Твоя задача:
        1. Сделай краткое конспект-саммари (выдели главные мысли bullet-points).
        2. Если есть формулы - напиши их в LaTeX.
        3. Составь 3 проверочных вопроса (тест) с вариантами ответов, чтобы проверить понимание.
        
        Оформи ответ красиво, используя Markdown.
        """

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Твой конспект", use_column_width=True)
            content = [base_prompt, image]
        elif user_question:
            content = [base_prompt, f"Текст/Тема для анализа: {user_question}"]
        
        if content:
            with st.spinner('ИИ думает... (это может занять пару секунд)'):
                try:
                    response = model.generate_content(content)
                    st.markdown(response.text)
                    st.success("Готово!")
                except Exception as e:
                    st.error(f"Произошла ошибка: {e}")
        else:
            st.warning("Пожалуйста, загрузи фото или напиши текст.")

# --- ФУТЕР ---
st.markdown("---")
st.caption("Прототип разработан для конкурса 'Студенческий стартап'. Работает на базе LLM.")
