import streamlit as st
import requests
from docx import Document
import io

# --- НАСТРОЙКИ ---
st.set_page_config(page_title="StudyFlow AI", layout="wide")
st.title("🎓 StudyFlow: Твой AI-помощник")

# --- ФУНКЦИЯ РАБОТЫ С ЯНДЕКСОМ (ЧЕРЕЗ HTTP) ---
def ask_yandex_gpt(text, api_key, folder_id):
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}"
    }
    payload = {
        "modelUri": f"gpt://{folder_id}/yandexgpt-lite",
        "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": "2000"},
        "messages": [
            {"role": "system", "text": "Ты — AI-тьютор. Сделай краткий конспект и тест из 3 вопросов."},
            {"role": "user", "text": text}
        ]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['result']['alternatives'][0]['message']['text']
    else:
        return f"Ошибка Яндекса: {response.text}"

# --- ФУНКЦИЯ СОЗДАНИЯ WORD ---
def create_docx(text):
    doc = Document()
    doc.add_heading('Конспект StudyFlow', 0)
    for line in text.split('\n'):
        doc.add_paragraph(line)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- ИНТЕРФЕЙС ---
user_text = st.text_area("Вставь сюда текст лекции:", height=250)

if st.button("🚀 Обработать"):
    if user_text:
        try:
            # Ключи берем из Secrets (они у тебя там уже есть)
            api_key = st.secrets["YC_API_KEY"]
            folder_id = st.secrets["YC_FOLDER_ID"]
            
            with st.spinner("Яндекс анализирует..."):
                result = ask_yandex_gpt(user_text, api_key, folder_id)
                st.markdown(result)
                
                if "Ошибка" not in result:
                    file = create_docx(result)
                    st.download_button("📥 Скачать Word", file, "konspekt.docx")
        except Exception as e:
            st.error(f"Произошла ошибка: {e}")
    else:
        st.warning("Сначала вставь текст!")
