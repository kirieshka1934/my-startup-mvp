import streamlit as st
import google.generativeai as genai
from PIL import Image
from docx import Document
import io

# --- НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="StudyFlow AI", layout="wide")

st.title("🎓 StudyFlow: Твой AI-помощник")
st.write("Загрузи фото конспекта, и я переведу его в текст + создам документ Word.")

# --- ПОДКЛЮЧЕНИЕ К GEMINI ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    # ИСПОЛЬЗУЕМ 1.5, ТАК КАК ОНА САМАЯ СТАБИЛЬНАЯ И БЕСПЛАТНАЯ
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error("Ошибка ключа API. Проверьте настройки Secrets.")

# --- ФУНКЦИЯ ДЛЯ СОЗДАНИЯ WORD ФАЙЛА ---
def create_docx(text):
    doc = Document()
    doc.add_heading('Конспект лекции (StudyFlow)', 0)
    # Разбиваем текст по строкам и добавляем в документ
    for line in text.split('\n'):
        doc.add_paragraph(line)
    
    # Сохраняем в виртуальную память (buffer), чтобы не создавать файл на диске
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- ИНТЕРФЕЙС ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Загрузка")
    uploaded_file = st.file_uploader("Фото конспекта (JPG, PNG)", type=["jpg", "png"])
    user_question = st.text_area("Дополнительный вопрос или тема:")
    generate_btn = st.button("🚀 Разобрать материал")

with col2:
    st.header("2. Результат")
    
    if generate_btn:
        prompt = ""
        content = []

        base_prompt = """
        Ты опытный студент-отличник. Твоя задача - перевести этот материал в идеальный конспект.
        1. Распознай весь текст (включая формулы в LaTeX).
        2. Структурируй его (Заголовки, списки).
        3. Исправь ошибки и дополни, если смысл теряется.
        """

        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Исходник", use_column_width=True)
            content = [base_prompt, image]
        elif user_question:
            content = [base_prompt, f"Тема: {user_question}"]
        
        if content:
            with st.spinner('ИИ читает почерк...'):
                try:
                    response = model.generate_content(content)
                    result_text = response.text
                    
                    # 1. Показываем текст на экране
                    st.markdown(result_text)
                    st.success("Готово!")
                    
                    # 2. Создаем файл для скачивания
                    docx_file = create_docx(result_text)
                    
                    # 3. Рисуем кнопку скачивания
                    st.download_button(
                        label="📄 Скачать конспект (.docx)",
                        data=docx_file,
                        file_name="konspekt_studyflow.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                    
                except Exception as e:
                    st.error(f"Произошла ошибка: {e}")
        else:
            st.warning("Загрузи что-нибудь!")
