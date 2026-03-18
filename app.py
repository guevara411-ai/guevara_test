import streamlit as st
import google.generativeai as genai
import PyPDF2
import docx

# --- إعدادات الواجهة الاحترافية ---
st.set_page_config(page_title="المُعلم الذكي PRO - جيفارا", page_icon="🎓", layout="wide")

# تصميم الألوان (CSS)
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stButton>button { background-color: #4CAF50; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- القائمة الجانبية ---
with st.sidebar:
    st.title("🎓 إعدادات جيفارا")
    api_key = st.text_input("🔑 مفتاح Gemini API الجديد:", type="password")
    st.divider()
    teacher_style = st.selectbox("🧠 شخصية المعلم:", ["المعلم المشجع", "المعلم الصارم", "وضع التلخيص"])
    if st.button("🗑️ مسح الذاكرة"):
        st.session_state.clear()
        st.rerun()

# --- عنوان التطبيق ---
st.title("🧠 المُعلم الذكي التفاعلي")
st.subheader("بإشراف المطور: جيفارا 🚀")

if api_key:
    try:
        genai.configure(api_key=api_key)
        # نستخدم الموديل الأكثر استقراراً في العالم حالياً
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        uploaded_file = st.file_uploader("📂 ارفع كتابك أو ملف الدراسة (PDF/DOCX):", type=['pdf', 'docx', 'txt'])

        if uploaded_file:
            if "file_text" not in st.session_state:
                with st.spinner('جاري قراءة محتوى الملف...'):
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
                    st.success("✅ تم تحميل الملف بنجاح!")

            # خانة الشات
            if "messages" not in st.session_state:
                st.session_state.messages = []

            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]): st.markdown(msg["content"])

            if prompt := st.chat_input("اسألني أي شيء عن الملف..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"): st.markdown(prompt)

                with st.chat_message("assistant"):
                    context = f"أنت {teacher_style}. استند لهذا النص في إجابتك: {st.session_state.file_text[:15000]}"
                    response = model.generate_content([context, prompt])
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})

    except Exception as e:
        st.error(f"⚠️ تنبيه: المفتاح قد يحتاج لتبديل أو المكتبة قيد التحديث. السبب: {str(e)}")
else:
    st.info("💡 يا هلا يا جيفارا! حط مفتاح الـ API في القائمة الجانبية عشان نبلش الدراسة.")

# --- التذييل ---
st.divider()
st.caption("تم التطوير بواسطة جيفارا | 2026 | النسخة الاحترافية المستقرة")
