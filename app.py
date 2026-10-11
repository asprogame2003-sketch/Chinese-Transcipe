import streamlit as st
import whisper
import os
import tempfile

st.title("🇨🇳 Chinese Transcription AI")
st.write("တရုတ်အသံဖိုင် (သို့) ဗီဒီယိုဖိုင်ကို တင်ပါ (Timestamp များပါဝင်မည်)")

# ဖိုင်တင်ရန် နေရာ
uploaded_file = st.file_uploader("ဖိုင်ရွေးချယ်ရန်", type=["mp3", "wav", "m4a", "mp4"])

if uploaded_file is not None:
    # တင်ထားသော အသံကို ဖွင့်နားထောင်နိုင်ရန်
    st.audio(uploaded_file)
    
    if st.button("စာသားအဖြစ် ပြောင်းမည်"):
        with st.spinner("AI ဖြင့် စာသားပြောင်းနေပါသည်... (မိနစ်အနည်းငယ် ကြာနိုင်ပါသည်)"):
            
            # ယာယီဖိုင်အဖြစ် သိမ်းဆည်းခြင်း
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # AI Model ကို ဆွဲတင်ပြီး တရုတ်ဘာသာစကားဖြင့် ပြောင်းခြင်း
            model = whisper.load_model("base")
            result = model.transcribe(tmp_path, language="zh")
            
            st.success("အောင်မြင်ပါသည်!")
            
            # Timestamp နှင့် စာသားများကို တွဲရန်
            full_text = ""
            for seg in result['segments']:
                start_time = int(seg['start'])
                minutes = start_time // 60
                seconds = start_time % 60
                time_str = f"[{minutes:02d}:{seconds:02d}]"
                full_text += f"{time_str} {seg['text']}\n"
                
            # စာသားများကို ဖော်ပြရန်
            st.text_area("📝 ရရှိလာသော စာသားများ", full_text, height=300)
            
            # ဒေါင်းလုဒ်လုပ်ရန် ခလုတ် (TXT ဖိုင်ဖြင့်)
            st.download_button(
                label="📄 စာသားများကို ဒေါင်းလုဒ်လုပ်မည်",
                data=full_text,
                file_name="Chinese_Transcription.txt",
                mime="text/plain"
            )