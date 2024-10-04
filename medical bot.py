import streamlit as m
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
import json
import os

# إعداد مفتاح API الخاص بك
GOOGLE_API_KEY = "AIzaSyCVHL_79gHlps9Ar_Dt3vTqc72YQNNvVcM"  # استبدل YOUR_API_KEY بمفتاحك الحقيقي
genai.configure(api_key=GOOGLE_API_KEY)

# إعداد قائمة لتخزين الرسائل
if 'messages' not in m.session_state:
    m.session_state.messages = []

# إعداد لتخزين المحادثات
if 'chat_history' not in m.session_state:
    m.session_state.chat_history = []

# إعداد حقل الإدخال
if 'user_input' not in m.session_state:
    m.session_state.user_input = ""

# عنوان التطبيق
m.title("الدردشة مع الذكاء الاصطناعي في مجال الطب")

# دالة لحفظ المحادثات في ملف JSON
def save_chat_history(chat_history):
    with open("chat_history.json", "w", encoding='utf-8') as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=4)

# دالة لتحميل المحادثات من ملف JSON إذا كان موجودًا
def load_chat_history():
    if os.path.exists("chat_history.json"):
        with open("chat_history.json", "r", encoding='utf-8') as f:
            return json.load(f)
    return []

# تحميل المحادثات السابقة
m.session_state.chat_history = load_chat_history()

# شريط جانبي لعرض المحادثات السابقة
with m.sidebar:
    m.markdown("### المحادثات السابقة")
    if m.session_state.chat_history:
        for idx, chat in enumerate(m.session_state.chat_history):
            m.markdown(f"#### محادثة {idx + 1}:")
            m.markdown(f"**أنت:** {chat['user']}")
            m.markdown(f"**إجابة:** {chat['bot']}")
            m.markdown("---")
    else:
        m.markdown("لا توجد محادثات سابقة.")

# واجهة المحادثة
m.markdown("### واجهة المحادثة")
for msg in m.session_state.messages:
    if msg['role'] == 'user':
        m.markdown(f"<div style='text-align: right; border: 2px solid blue; padding: 10px; border-radius: 5px; background-color: #f0f8ff; margin-bottom: 10px;'>**سؤال:** {msg['text']}</div>", unsafe_allow_html=True)
    elif msg['role'] == 'bot':
        m.markdown(f"<div style='text-align: left; border: 2px solid green; padding: 10px; border-radius: 5px; background-color: #e6ffe6; margin-bottom: 10px;'>**إجابة:** {msg['text']}</div>", unsafe_allow_html=True)

# حقل إدخال النص
user_input = m.text_input("اكتب سؤالك هنا...", value=m.session_state.user_input)

# إنشاء الأعمدة للأزرار
col1, col2 = m.columns([1, 1])  # تخصيص الأعمدة بالتساوي

# دالة لإرسال السؤال
def send_question(user_input):
    if user_input:
        # إضافة رسالة المستخدم إلى الحالة
        m.session_state.messages.append({'role': 'user', 'text': user_input})

        # عرض السؤال فورًا بعد الإرسال
        m.markdown(f"<div style='text-align: right; border: 2px solid blue; padding: 10px; border-radius: 5px; background-color: #f0f8ff; margin-bottom: 10px;'>**سؤال:** {user_input}</div>", unsafe_allow_html=True)

        # تمرير السؤال مباشرةً إلى نموذج الذكاء الاصطناعي
        prompt = f"أجب على أي سؤال متعلق بالطب وإن كان السؤال ليس له علاقة بالطب قدم اعتذارك عن الاجابة ووضح أنك مخصص فقط للرد على الأسئلة المتعلقة بالطب: {user_input}"
        response = genai.GenerativeModel('gemini-pro').generate_content(prompt)

        # إضافة الرد إلى الرسائل
        m.session_state.messages.append({'role': 'bot', 'text': response.text})

        # تحويل النص إلى صوت
        tts = gTTS(response.text, lang='ar')
        tts.save("response.mp3")
        m.audio("response.mp3", format="audio/mp3", start_time=0)

        # عرض الرد بعد السؤال
        m.markdown(f"<div style='text-align: left; border: 2px solid green; padding: 10px; border-radius: 5px; background-color: #e6ffe6; margin-bottom: 10px;'>**إجابة:** {response.text}</div>", unsafe_allow_html=True)

        # حفظ المحادثة
        m.session_state.chat_history.append({'user': user_input, 'bot': response.text})
        save_chat_history(m.session_state.chat_history)

        # إعادة تعيين حقل الإدخال
        m.session_state.user_input = ""  # حذف السؤال من خانة الكتابة

# زر الإرسال
with col1:
    if m.button("إرسال"):
        send_question(user_input)

# زر الإدخال الصوتي
with col2:
    if m.button("استخدام الإدخال الصوتي"):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            m.markdown("### استمع للرسالة...")
            audio_data = recognizer.listen(source)
            m.markdown("### معالجة الصوت...")
            try:
                user_input_audio = recognizer.recognize_google(audio_data, language='ar-SA')
                # تخزين الإدخال الصوتي في session_state
                m.session_state.user_input = user_input_audio  # تخزين الإدخال الصوتي
                send_question(user_input_audio)  # إرسال السؤال مباشرة
            except sr.UnknownValueError:
                m.error("لم يتم التعرف على الصوت.")
            except sr.RequestError:
                m.error("حدثت مشكلة في الاتصال بخدمة التعرف على الصوت.")

# تحديث حقل الإدخال بعد إعادة التحميل
if m.session_state.user_input:
    user_input ="" # استخدام القيمة المخزنة في session_state

# تثبيت الحقول في الجزء السفلي
m.markdown("<style>.stTextInput { position: fixed; bottom: 40px; width: 100%; }</style>", unsafe_allow_html=True)
m.markdown("<style>.stButton { position: fixed; bottom: 0; width: 100%; }</style>", unsafe_allow_html=True)