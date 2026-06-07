import streamlit as st
import google.generativeai as genai

# 1. 頁面設定
st.set_page_config(page_title="AI 海龜湯防禦系統", page_icon="🐢", layout="centered")

# 2. 獲取 API 金鑰
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("請在 Streamlit Secrets 設定 GEMINI_API_KEY")
    st.stop()

# 3. 最標準的 SDK 初始化 (不帶任何額外路徑參數)
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def call_gemini_api(prompt_text):
    # 使用 SDK 內建的呼叫方式，它會自動處理 v1 路徑
    response = model.generate_content(prompt_text)
    return response.text

# 4. 遊戲介面邏輯
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.target_answer = ""
    st.session_state.chat_history = []

st.title("🐢 AI 海龜湯防禦系統")

if not st.session_state.game_started:
    if st.button("🎲 秘密生成謎底並開始遊戲", use_container_width=True):
        with st.spinner("AI 生成謎底中..."):
            try:
                secret_word = call_gemini_api("請選一個物品作為謎底。只輸出名稱。").strip()
                st.session_state.target_answer = secret_word
                st.session_state.game_started = True
                st.rerun()
            except Exception as e:
                st.error(f"初始化錯誤：{e}")
else:
    st.warning(f"🤫 後台謎底：**{st.session_state.target_answer}**")
    if st.button("🔄 重置遊戲"):
        st.session_state.game_started = False
        st.rerun()

    # 顯示對話
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    if user_input := st.chat_input("請輸入提問..."):
        with st.chat_message("user"):
            st.write(user_input)
        
        # 防禦機制
        defense_prompt = f"謎底是：{st.session_state.target_answer}。只能回答「是」、「不是」、「與故事/題目無關」或「不完全是」。玩家提問：{user_input}"
        
        with st.chat_message("assistant"):
            try:
                res = call_gemini_api(defense_prompt).strip()
                st.write(res)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": res})
            except Exception as e:
                st.error(f"判定錯誤：{e}")
