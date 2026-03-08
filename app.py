import streamlit as st
import yandexcloud
from yandex.cloud.ai.foundation_models.v1.foundation_models_service_pb2 import CompletionRequest
from yandex.cloud.ai.foundation_models.v1.foundation_models_service_pb2_grpc import TextGenerationServiceStub
from yandex.cloud.ai.foundation_models.v1.foundation_models_pb2 import CompletionOptions, Message
from docx import Document
import io

# --- НАСТРОЙКИ ---
st.set_page_config(page_title="StudyFlow AI", layout="wide")
st.title("🎓 StudyFlow: Твой AI-помощник (YandexGPT)")

# --- ФУНКЦИЯ РАБОТЫ С ЯНДЕКСОМ ---
def ask_yandex(text, api_key, folder_id):
    sdk = yandexcloud.SDK(api_key=api_key)
    service = sdk.client(TextGenerationServiceStub)
    
    request = CompletionRequest(
        model_uri=f"gpt://{folder_id}/yandexgpt-lite/latest",
        completion_options=CompletionOptions(temperature=0.6, max_tokens=2000),
        messages=[
            Message(role="system", text="Ты — AI-тьютор. Сделай краткий конспект и тест из 3 вопросов по тексту."),
            Message(role="user", text=text)
        ]
    )
    
    res = service.Completion(request)
    return res.alternatives[0].message.text

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
            # Берем ключи из Secrets
            api_key = st.secrets["YC_API_KEY"]
            folder_id = st.secrets["YC_FOLDER_ID"]
            
            with st.spinner("Яндекс думает..."):
                result = ask_yandex(user_text, api_key, folder_id)
                st.markdown(result)
                
                # Кнопка скачивания
                file = create_docx(result)
                st.download_button("📥 Скачать Word", file, "konspekt.docx")
        except Exception as e:
            st.error(f"Ошибка: {e}")
    else:
        st.warning("Сначала вставь текст!")
