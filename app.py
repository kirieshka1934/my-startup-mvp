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
    # ИСПОЛЬЗУЕМ ДРУГУЮ, БОЛЕЕ СТАБИЛЬНУЮ МОДЕЛЬ, СПЕЦИАЛЬНО ДЛЯ КАРТИНОК
    model = genai.GenerativeModel('gemini-pro')
except Exception as e:
    st.error(f"Ошибка ключа API. Проверьте настройки Secrets. {e}")

# --- ФУНКЦИЯ ДЛЯ СОЗДАНИЯ WORD ФАЙЛА ---
def create_docx(text):
    doc = Document()
    doc.add_heading('Конспект (StudyFlow)', 0)
    for line in text.split('\n'):
        doc.add_paragraph(line)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- ИНТЕРФЕЙС ---
col1, col2 = st.columns(2)

with col1:
    st.header("1. Загрузка")
    uploaded_file = st.file_uploader("Фото конспекта (JPG, PNG)", type=["jpg", "png"])
    generate_btn = st.button("🚀 Разобрать материал")

with col2:
    st.header("2. Результат")
    
    if generate_btn and uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Исходник", use_column_width=True)

        with st.spinner('ИИ думает...'):
            try:
                # Упрощаем запрос: отправляем только картинку и простой текст
                response = model.generate_content([
                    "Распознай этот рукописный текст. Если видишь математические формулы, оформи их в формате LaTeX.", 
                    image
                ])
                
                result_text = response.text
                st.markdown(result_text)
                st.success("Готово!")
                
                docx_file = create_docx(result_text)
                st.download_button(
                    label="📄 Скачать конспект (.docx)",
                    data=docx_file,
                    file_name="konspekt_studyflow.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
                
            except Exception as e:
                st.error(f"Произошла ошибка: {e}")
    elif generate_btn and uploaded_file is None:
        st.warning("Пожалуйста, загрузи фото!")
