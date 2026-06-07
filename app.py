import streamlit as st
from google import genai
import time

# 設定網頁介面
st.set_page_config(page_title="AI 海龜湯防禦系統", page_icon="🐢", layout="centered")

# 從 Streamlit Secrets 讀取金鑰
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("請在 Streamlit Secrets 中設定 GEMINI_API_KEY")
    st.stop()

# 使用 SDK 初始化 (這會自動處理驗證與 API 路由)
client = genai.Client(api_key=api_key)

def call_gemini_api(prompt_text):
    # 使用 SDK 的標準呼叫方式，避開所有網址錯誤
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt_text
    )
    return response.text

# 遊戲狀態管理
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.target_answer = ""
    st.session_state.chat_history = []

st.title("🐢 AI 海龜湯防禦系統")

# 開始遊戲按鈕
if not st.session_state.game_started:
    if st.button("🎲 生成謎底並開始遊戲"):
        with st.spinner("AI 生成中..."):
            try:
                # 定義謎底生成
                secret_prompt = "請隨機秘密挑選一個明確的物品（如水果、運動、用品）作為海龜湯謎底，只需輸出物品名稱。"
                st.session_state.target_answer = call_gemini_api(secret_prompt).strip()
                st.session_state.game_started = True
                st.rerun()
            except Exception as e:
                st.error(f"初始化失敗：{e}")
else:
    st.warning(f"秘密謎底：{st.session_state.target_answer}")
    
    # 對話邏輯
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    if user_input := st.chat_input("請提問..."):
        with st.chat_message("user"):
            st.write(user_input)
            
        defense_prompt = f"""
        你是嚴格裁判。謎底是：{st.session_state.target_answer}。
        只能回答「是」、「不是」、「與故事/題目無關」或「不完全是」。
        絕對禁止洩漏謎底。
        玩家提問：{user_input}
        """
        
        with st.chat_message("assistant"):
            try:
                res = call_gemini_api(defense_prompt).strip()
                st.write(res)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": res})
            except Exception as e:
                st.error(f"連線失敗：{e}")
