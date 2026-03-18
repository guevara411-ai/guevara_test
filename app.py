import streamlit as st
import PyPDF2
import docx
import google.generativeai as genai

# --- إعدادات الصفحة الاحترافية ---
st.set_page_config(
    page_title="المُعلم الذكي PRO",
    page_icon="🎓",
    layout="wide"
)

# --- تنسيق الواجهة (CSS) لجعلها أجمل ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #4CAF50; color: white; }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- إعداد متغيرات الجلسة ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "file_text" not in st.session_state:
    st.session_state.file_text = ""

# --- القائمة الجانبية (Sidebar) للإعدادات ---
with st.sidebar:
    st.title("⚙️ إعدادات المعلم")
    api_key = st.text_input("🔑 مفتاح Gemini API:", type="password")
    
    st.divider()
    
    teacher_style = st.selectbox(
        "🧠 اختر شخصية المعلم:",
        ["المعلم الصارم (أسئلة صعبة)", "المعلم المشجع (شرح مبسط)", "وضع المراجعة السريعة"]
    )
    
    learning_mode = st.radio(
        "🎯 وضع التعلم:",
        ["سؤال وجواب (اختبار)", "شرح ومناقشة", "تلخيص شامل"]
    )
    
    if st.button("🗑️ مسح المحادثة"):
        st.session_state.messages = []
        st.session_state.chat_session = None
        st.rerun()

# --- واجهة التطبيق الرئيسية ---
st.title("🎓 المُعلم الذكي التفاعلي (النسخة المطورة)")
st.info("ارفع ملفك الدراسي، وسأقوم بتحليله واختبارك بناءً على الوضع الذي اخترته.")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    # --- رفع الملف ---
    uploaded_file = st.file_uploader("📂 ارفع ملف (PDF, DOCX, TXT):", type=['pdf', 'docx', 'txt'])

    if uploaded_file and not st.session_state.file_text:
        with st.spinner('جاري تحليل المحتوى بعمق...'):
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
            
            # تعليمات الذكاء الاصطناعي المطورة
            prompt_instruction = f"""
            أنت الآن تؤدي دور: {teacher_style}.
            وضع التعلم الحالي هو: {learning_mode}.
            محتوى الكتاب أو النص هو:
            {text[:25000]}
            
            قواعدك:
            1. إذا كان الوضع 'سؤال وجواب'، اطرح سؤالاً ذكياً واحداً وانتظر الإجابة.
            2. إذا كان الوضع 'شرح'، فسر المفاهيم الصعبة بأسلوب {teacher_style}.
            3. دائماً صحح الأخطاء بدقة واذكر الصفحة أو السياق إذا أمكن.
            4. استخدم الرموز التعبيرية لجعل الحوار تفاعلياً.
            """
            
            st.session_state.chat_session = model.start_chat(history=[
                {"role": "user", "parts": [prompt_instruction]}
            ])
            
            # البداية
            initial_msg = "مرحباً! لقد قرأت الملف بالكامل. كيف تحب أن نبدأ اليوم؟"
            st.session_state.messages.append({"role": "assistant", "content": initial_msg})

    # --- عرض المحادثة ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # --- إدخال المستخدم ---
    if prompt := st.chat_input("أجب هنا أو اسأل عن شيء في الملف..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if st.session_state.chat_session:
                response = st.session_state.chat_session.send_message(prompt)
                full_response = response.text
                st.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.warning("يرجى رفع ملف أولاً للبدء.")

else:
    st.warning("⚠️ من فضلك أدخل مفتاح API في القائمة الجانبية للبدء.")

# --- تذييل الصفحة ---
st.divider()
st.caption("تم التطوير بواسطة جيفارا | بدعم من Gemini AI")
