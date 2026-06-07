import streamlit as st
import google.generativeai as genai
import time

# 1. 初始化設定
st.set_page_config(page_title="AI 海龜湯防禦系統", page_icon="🐢")

# 2. 強制設定金鑰
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. 強制指定模型，使用 gemini-1.5-flash
model = genai.GenerativeModel('gemini-1.5-flash')

def call_gemini_api(prompt_text):
    # 使用標準 generate_content，這是目前最穩定的呼叫方式
    response = model.generate_content(prompt_text)
    return response.text

# 4. 遊戲邏輯 (與之前一致)
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.target_answer = ""
    st.session_state.chat_history = []

st.title("🐢 AI 海龜湯防禦系統")

if not st.session_state.game_started:
    if st.button("🎲 秘密生成謎底並開始遊戲"):
        with st.spinner("AI 正在秘密構思謎底..."):
            try:
                # 簡化 Prompt 避免複雜路徑解析問題
                secret_word = call_gemini_api("請回答一個生活物品名稱，不要有其他字。").strip()
                st.session_state.target_answer = secret_word
                st.session_state.game_started = True
                st.rerun()
            except Exception as e:
                st.error(f"初始化失敗 (Error: {e})")
else:
    st.warning(f"秘密謎底：{st.session_state.target_answer}")
    # (其餘對話邏輯保持不變)
