import streamlit as st
import PyPDF2
import docx
import google.generativeai as genai
import time

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="المُعلم العملاق 4.0", page_icon="🎓", layout="wide")

# تخصيص التصميم عبر CSS
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #4A90E2; color: white; }
    .report-card { padding: 20px; border-radius: 15px; background-color: #ffffff; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- إدارة حالة الجلسة (Session State) ---
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "score" not in st.session_state:
    st.session_state.score = {"correct": 0, "total": 0}
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "متوسط"
if "student_level" not in st.session_state:
    st.session_state.student_level = "مبتدئ"

# --- الواجهة الجانبية (Sidebar) ---
with st.sidebar:
    st.title("⚙️ إعدادات المعلم")
    api_key = st.text_input("🔑 مفتاح Gemini API:", type="password")
    
    st.divider()
    st.subheader("📊 لوحة الأداء")
    col1, col2 = st.columns(2)
    col1.metric("الأسئلة", st.session_state.score["total"])
    col2.metric("الإجابات الصحيحة", st.session_state.score["correct"])
    
    st.divider()
    st.session_state.difficulty = st.select_slider(
        "🎯 مستوى صعوبة الأسئلة:",
        options=["سهل", "متوسط", "تحدي", "عبقري"]
    )
    
    if st.button("🗑️ مسح الذاكرة والبدء من جديد"):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# --- دالة استخراج النص ---
def extract_text(file):
    text = ""
    if file.name.endswith('.txt'):
        text = file.read().decode("utf-8")
    elif file.name.endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
    elif file.name.endswith('.docx'):
        doc = docx.Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    return text

# --- المنطق الأساسي ---
st.title("🎓 المُعلم الذكي التفاعلي (النسخة الاحترافية)")

if not api_key:
    st.warning("👈 من فضلك، أدخل مفتاح API في اللوحة الجانبية للبدء.")
else:
    genai.configure(api_key=api_key)
    # استخدام موديل Pro للعمق التحليلي أو Flash للسرعة
    model = genai.GenerativeModel('gemini-1.5-pro') 

    if st.session_state.chat_session is None:
        uploaded_file = st.file_uploader("📂 ارفع منهجك الدراسي (PDF, DOCX, TXT)", type=['pdf', 'docx', 'txt'])
        
        if uploaded_file:
            with st.spinner('🧠 يقوم المعلم الآن بقراءة الكتاب وتحليله بدقة...'):
                raw_text = extract_text(uploaded_file)
                
                # بناء البرومبت "العميق"
                system_instruction = f"""
                أنت "المعلم الأكاديمي المتقدم". هذا هو المحتوى الذي ستدرسه:
                {raw_text[:30000]} 

                قواعد التدريس الخاصة بك:
                1. الشخصية: معلم محفز، دقيق جداً، يستخدم أمثلة من الواقع.
                2. المنهجية: استخدم "تصنيف بلوم". ابدأ بأسئلة الفهم ثم انتقل للتحليل والنقد بناءً على مستوى الصعوبة: {st.session_state.difficulty}.
                3. التقييم: عندما يجيب المستخدم، حلل إجابته (هل هي دقيقة؟ ناقصة؟ خاطئة؟).
                4. التغذية الراجعة: لا تقل "صح" أو "خطأ" فقط. اشرح "لماذا" واستخرج فقرات من النص تدعم شرحك.
                5. التفاعل: اطرح سؤالاً واحداً فقط في كل مرة.
                6. التنسيق: استخدم Bold للجمل المهمة، ورموز تعبيرية لتسهيل القراءة.

                ابدأ الآن بالترحيب بالطالب وطرح أول سؤال بناءً على مستوى الصعوبة المحدد.
                """
                
                st.session_state.chat_session = model.start_chat(history=[])
                response = st.session_state.chat_session.send_message(system_instruction)
                
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                st.rerun()

    else:
        # عرض المحادثة
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # إدخال المستخدم
        if prompt := st.chat_input("أجب على السؤال هنا..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("🤔 أفكر في إجابتك وأقارنها بالمصدر..."):
                    # إرسال مستوى الصعوبة الحالي مع كل إجابة لضمان التكيف
                    context_query = f"إجابتي هي: {prompt}. قيمها بدقة بناءً على النص، ثم اطرح السؤال التالي بمستوى صعوبة {st.session_state.difficulty}."
                    response = st.session_state.chat_session.send_message(context_query)
                    
                    # محاكاة بسيطة لتتبع النقاط (يمكن جعلها أعقد عبر تحليل الرد)
                    st.session_state.score["total"] += 1
                    if "صحيح" in response.text or "أحسنت" in response.text:
                        st.session_state.score["correct"] += 1
                        
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
            
            # تحديث الواجهة الجانبية فورياً
            st.sidebar.empty() 
