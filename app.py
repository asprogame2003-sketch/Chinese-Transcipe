import streamlit as st
import whisper
import os
import tempfile
import base64

# Streamlit Page Config (Logo နှင့် နာမည်ထည့်ရန်)
st.set_page_config(page_title="Storyloopmm Transcription", page_icon="📝", layout="wide")

# PDF ထုတ်ရန် HTML Template ကို ပြင်ဆင်ခြင်း
def create_pdf_html(text):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="utf-8">
    <title>Transcription</title>
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        h1 {{ color: #d32f2f; }}
        p {{ line-height: 1.6; white-space: pre-wrap; }}
    </style>
    </head>
    <body>
        <h1>Storyloopmm - Chinese Transcription</h1>
        <p>{text}</p>
    </body>
    </html>
    """
    return html_content

# Session State (Refresh မလုပ်မချင်း စာသားတွေ ပျောက်မသွားအောင် သိမ်းထားပေးမည့်စနစ်)
if "transcript_result" not in st.session_state:
    st.session_state.transcript_result = ""
if "audio_bytes" not in st.session_state:
    st.session_state.audio_bytes = None

# Logo နှင့် YouTube Link
st.markdown("""
<div style="text-align: center;">
    <h1 style="color: #d32f2f;">📝 Storyloopmm Transcription</h1>
    <a href="https://youtube.com/@storyloopmm?si=gIas6N8QkOS4CcBV" target="_blank" style="text-decoration: none; color: white; background-color: #FF0000; padding: 8px 15px; border-radius: 5px; font-weight: bold;">▶️ YouTube Channel သို့ သွားရန်</a>
</div>
<hr>
""", unsafe_allow_html=True)

st.write("တရုတ်အသံဖိုင် (သို့) ဗီဒီယိုဖိုင်ကို တင်ပါ (Timestamp များပါဝင်မည်)")

# ဖိုင်တင်ရန် နေရာ (3GB အထိ တင်နိုင်ရန် config တွင် ပြင်ဆင်ရမည်)
uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ရန် (Video သို့မဟုတ် Audio)", type=["mp3", "wav", "m4a", "mp4", "mkv", "mov"])

if uploaded_file is not None:
    st.session_state.audio_bytes = uploaded_file.getvalue()
    st.audio(st.session_state.audio_bytes)
    
    if st.button("စာသားအဖြစ် ပြောင်းမည်"):
        with st.spinner("AI ဖြင့် စာသားပြောင်းနေပါသည်... (ဖိုင်ကြီးပါက အချိန်ကြာနိုင်ပါသည်)"):
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # AI Model ဆွဲတင်ခြင်း
            model = whisper.load_model("base")
            result = model.transcribe(tmp_path, language="zh")
            
            # Timestamp များနှင့် စာသားများကို စီစဉ်ခြင်း
            full_text = ""
            for seg in result['segments']:
                start_time = int(seg['start'])
                minutes = start_time // 60
                seconds = start_time % 60
                time_str = f"[{minutes:02d}:{seconds:02d}]"
                full_text += f"{time_str} {seg['text']}\n"
            
            # Result ကို Session State ထဲ သိမ်းခြင်း
            st.session_state.transcript_result = full_text
            st.success("အောင်မြင်ပါသည်!")

# Session State တွင် စာသားရှိနေပါက အမြဲပြနေမည် (Refresh မလုပ်မချင်း မပျောက်ပါ)
if st.session_state.transcript_result:
    st.text_area("📝 ရရှိလာသော စာသားများ", st.session_state.transcript_result, height=400)
    
    # HTML/PDF အဖြစ် Save လုပ်ရန် အလွယ်ကူဆုံးနည်းလမ်း
    html_data = create_pdf_html(st.session_state.transcript_result)
    b64 = base64.b64encode(html_data.encode()).decode()
    
    # ဒေါင်းလုဒ် ခလုတ်များ
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📄 TXT ဖိုင်ဖြင့် ဒေါင်းလုဒ်လုပ်မည်",
            data=st.session_state.transcript_result,
            file_name="Storyloopmm_Transcription.txt",
            mime="text/plain"
        )
    with col2:
        # Browser မှတဆင့် Print to PDF လုပ်နိုင်ရန် HTML ဖိုင်ပေးခြင်း (Streamlit တွင် အလွယ်ဆုံး PDF ထုတ်နည်း)
        href = f'<a href="data:text/html;base64,{b64}" download="Storyloopmm_Transcription.html" style="text-decoration: none; background-color: #4CAF50; color: white; padding: 8px 15px; border-radius: 4px; display: inline-block;">📄 PDF (HTML) ထုတ်ရန် ဒေါင်းလုဒ်ဆွဲပါ</a>'
        st.markdown(href, unsafe_allow_html=True)
        st.caption("ဒေါင်းလုဒ်ရလာသော ဖိုင်ကို Browser ဖြင့်ဖွင့်ပြီး Ctrl+P နှိပ်၍ 'Save as PDF' ဖြင့် သိမ်းပါ။")
