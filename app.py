import streamlit as st
import PyPDF2
import docx
import google.generativeai as genai

# إعداد واجهة الصفحة
st.set_page_config(page_title="المُعلم الذكي التفاعلي", page_icon="🧠", layout="centered")
st.title("🧠 المُعلم الذكي التفاعلي")
st.markdown("ارفع ملفك، وسأقوم باختبارك سؤالاً بسؤال. أجبني وسأصحح لك وأشرح لك التفاصيل!")

# إعداد متغيرات الجلسة (للاحتفاظ بالذاكرة والمحادثة)
if "chat_session" not in st.session_state:
    st.session_state.chat_session = None
if "file_processed" not in st.session_state:
    st.session_state.file_processed = False
if "messages" not in st.session_state:
    st.session_state.messages = []

# إدخال مفتاح API
api_key = st.text_input("🔑 أدخل مفتاح Gemini API الخاص بك:", type="password")

if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    # الخطوة 1: رفع الملف ومعالجته (تظهر فقط إذا لم يتم معالجة ملف بعد)
    if not st.session_state.file_processed:
        uploaded_file = st.file_uploader("📂 ارفع الملف (TXT, PDF, DOCX)...", type=['txt', 'pdf', 'docx'])

        if uploaded_file is not None:
            text = ""
            with st.spinner('جاري قراءة الملف...'):
                try:
                    if uploaded_file.name.endswith('.txt'):
                        text = uploaded_file.read().decode("utf-8")
                    elif uploaded_file.name.endswith('.pdf'):
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            extracted = page.extract_text()
                            if extracted: text += extracted + "\n"
                    elif uploaded_file.name.endswith('.docx'):
                        doc = docx.Document(uploaded_file)
                        for para in doc.paragraphs:
                            text += para.text + "\n"

                    if text.strip():
                        # إنشاء التعليمات المعقدة للذكاء الاصطناعي
                        system_instruction = f"""
                        أنت معلم خبير وصارم ولكنك مشجع. هذا هو النص الدراسي:
                        {text[:20000]}
                        
                        مهمتك:
                        1. اطرح سؤالاً واحداً فقط لاختبار فهمي للنص.
                        2. انتظر إجابتي.
                        3. بعد أن أجيب، قيّم إجابتي (صحيحة، خاطئة، غير مكتملة).
                        4. اشرح لي الإجابة الصحيحة أو لماذا أخطأت بناءً على النص.
                        5. ثم اطرح السؤال التالي مباشرة.
                        لا تطرح أكثر من سؤال في نفس الرسالة أبداً.
                        """
                        
                        # بدء جلسة محادثة مع ذاكرة
                        st.session_state.chat_session = model.start_chat(history=[
                            {"role": "user", "parts": [system_instruction]}
                        ])
                        
                        # طلب السؤال الأول من الـ AI
                        first_response = st.session_state.chat_session.send_message("مرحباً أيها المعلم، أنا جاهز. اطرح السؤال الأول.")
                        
                        # حفظ الرسالة الأولى في الذاكرة لعرضها
                        st.session_state.messages = [{"role": "assistant", "content": first_response.text}]
                        st.session_state.file_processed = True
                        st.rerun() # تحديث الصفحة لإظهار واجهة المحادثة
                        
                except Exception as e:
                    st.error(f"❌ حدث خطأ: {e}")

    # الخطوة 2: واجهة المحادثة التفاعلية (تظهر بعد قراءة الملف)
    if st.session_state.file_processed:
        st.success("✅ الملف في ذاكرتي الآن. دعنا نبدأ الاختبار!")
        
        # عرض سجل المحادثة
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        
        # مربع إدخال إجابة المستخدم
        user_answer = st.chat_input("اكتب إجابتك هنا...")
        
        if user_answer:
            # عرض إجابة المستخدم
            st.session_state.messages.append({"role": "user", "content": user_answer})
            with st.chat_message("user"):
                st.markdown(user_answer)
            
            # إرسال الإجابة للذكاء الاصطناعي للحصول على التقييم والسؤال التالي
            with st.chat_message("assistant"):
                with st.spinner("جاري تقييم إجابتك..."):
                    response = st.session_state.chat_session.send_message(user_answer)
                    st.markdown(response.text)
            
            # حفظ رد الـ AI في الذاكرة
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        # زر لإعادة تعيين التطبيق ورفع ملف جديد
        if st.button("🔄 إنهاء الاختبار ورفع ملف جديد"):
            st.session_state.file_processed = False
            st.session_state.chat_session = None
            st.session_state.messages = []
            st.rerun()
else:
    st.info("👈 يرجى إدخال مفتاح API للبدء.")