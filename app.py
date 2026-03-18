import streamlit as st
import google.generativeai as genai
import PyPDF2

st.set_page_config(page_title="Gevaara AI Pro")

st.title("🎓 المعلم الذكي - نسخة جيفارا")

# القائمة الجانبية
with st.sidebar:
    api_key = st.text_input("🔑 حط المفتاح هون:", type="password")
    st.warning("إذا طلع خطأ، تأكد من المفتاح")

if api_key:
    try:
        genai.configure(api_key=api_key)
        
        # هاد هو الاسم "الرسمي" اللي مستحيل يعطي 404 هسا
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        uploaded_file = st.file_uploader("ارفع ملف PDF:", type=['pdf'])
        
        if uploaded_file:
            reader = PyPDF2.PdfReader(uploaded_file)
            text = "".join([p.extract_text() for p in reader.pages])
            
            prompt = st.chat_input("اسألني أي شيء عن الكتاب...")
            
            if prompt:
                with st.chat_message("user"): st.markdown(prompt)
                
                # إرسال السؤال مع النص
                response = model.generate_content(f"سياق الكتاب: {text[:15000]}\n\nالسؤال: {prompt}")
                
                with st.chat_message("assistant"):
                    st.markdown(response.text)
                    
    except Exception as e:
        st.error(f"حدث خطأ تقني: {str(e)}")
else:
    st.info("يا جيفارا، حط المفتاح على الشمال عشان نبلش.")
