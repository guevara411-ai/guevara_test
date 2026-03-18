import streamlit as st
import PyPDF2
import docx
import google.generativeai as genai

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المُعلم الذكي PRO", page_icon="🎓", layout="wide")

# --- كود التصحيح الذاتي للموديل ---
def get_working_model(api_key):
    genai.configure(api_key=api_key)
    # قائمة بالموديلات المرتبة من الأحدث للأضمن
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.5-pro',
        'models/gemini-1.5-flash',
        'gemini-pro'
    ]
    for model_name in models_to_try:
        try:
            model = genai.GenerativeModel(model_name)
            # تجربة وهمية للتأكد أن الموديل متاح
            model.generate_content("test", generation_config={"max_output_tokens": 1})
            return model
        except Exception:
            continue
    return None

# --- تحضير الجلسة ---
if "messages" not in st.session_state: st.session_state.messages = []
if "chat_session" not in st.session_state: st.session_state.chat_session = None
if "file_text" not in st.session_state: st.session_state.file_text = ""

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("⚙️ الإعدادات")
    api_key = st.text_input("🔑 مفتاح Gemini API:", type="password")
    st.divider()
    teacher_style = st.selectbox("🧠 شخصية المعلم:", ["المعلم الصارم", "المعلم المشجع", "وضع المراجعة"])
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()

# --- الواجهة الرئيسية ---
st.title("🎓 المُعلم الذكي (النسخة المستقرة)")

if api_key:
    # محاولة تشغيل الموديل بنظام "التصحيح الذاتي"
    model = get_working_model(api_key)
    
    if model:
        uploaded_file = st.file_uploader("📂 ارفع ملفك الدراسي:", type=['pdf', 'docx', 'txt'])

        if uploaded_file and not st.session_state.file_text:
            with st.spinner('جاري التحليل...'):
                text = ""
                if uploaded_file.name.endswith('.pdf'):
                    reader = PyPDF2.PdfReader(uploaded_file)
                    for page in reader.pages: text += page.extract_text() + "\n"
                elif uploaded_file.name.endswith('.docx'):
                    doc = docx.Document(uploaded_file)
                    for p in doc.paragraphs: text += p.text + "\n"
                else:
                    text = uploaded_file.read().decode("utf-8")
                
                st.session_state.file_text = text
                prompt_init = f"أنت {teacher_style}. محتوى الملف: {text[:20000]}. ابدأ باختباري بسؤال واحد."
                st.session_state.chat_session = model.start_chat(history=[])
                response = st.session_state.chat_session.send_message(prompt_init)
                st.session_state.messages.append({"role": "assistant", "content": response.text})

        # عرض الرسائل
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]): st.markdown(msg["content"])

        # إدخال المستخدم
        if prompt := st.chat_input("اسأل أو أجب هنا..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            try:
                response = st.session_state.chat_session.send_message(prompt)
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"حدث خطأ في الاتصال: {e}")
    else:
        st.error("❌ عذراً، مفتاح API الخاص بك لا يدعم الموديلات الحالية أو هناك مشكلة في الاتصال بجوجل.")
else:
    st.warning("⚠️ يرجى إدخال المفتاح في القائمة الجانبية.")
