import streamlit as st
import requests
import json
import time

# 1. 初始化頁面
st.set_page_config(page_title="AI 海龜湯防禦系統", page_icon="🐢", layout="centered")

# 2. 讀取 Secrets 中的 API 金鑰
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("請在 Streamlit Secrets 設定 GEMINI_API_KEY")
    st.stop()

# 3. 核心 API 呼叫函式 (直接透過 POST 控制路由)
def call_gemini_api(prompt_text):
    # 【關鍵修正】：直接指定 v1 正式版路徑，繞過 SDK 的自動路由錯誤
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}]
    }
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        res_json = response.json()
        return res_json["candidates"][0]["content"]["parts"][0]["text"]
    else:
        raise Exception(f"API 呼叫失敗 (狀態碼 {response.status_code}): {response.text}")

# 4. 遊戲邏輯與顯示
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.target_answer = ""
    st.session_state.chat_history = []

st.title("🐢 AI 海龜湯防禦系統")

if not st.session_state.game_started:
    if st.button("🎲 秘密生成謎底並開始遊戲", use_container_width=True):
        with st.spinner("AI 正在秘密構思謎底..."):
            try:
                secret_prompt = "請從【球類運動】、【水果】、【生活用品】中挑一個作為謎底。請只輸出物品名稱，不要有標點。"
                st.session_state.target_answer = call_gemini_api(secret_prompt).strip()
                st.session_state.game_started = True
                st.rerun()
            except Exception as e:
                st.error(f"初始化錯誤：{e}")
else:
    st.warning(f"🤫 後台謎底：**{st.session_state.target_answer}**")
    
    if st.button("🔄 重置遊戲"):
        st.session_state.game_started = False
        st.rerun()

    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    if user_input := st.chat_input("請輸入提問..."):
        with st.chat_message("user"):
            st.write(user_input)
        
        defense_prompt = f"謎底是：{st.session_state.target_answer}。只能回答「是」、「不是」、「與故事/題目無關」或「不完全是」。玩家提問：{user_input}"
        
        with st.chat_message("assistant"):
            try:
                res = call_gemini_api(defense_prompt).strip()
                st.write(res)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": res})
            except Exception as e:
                st.error(f"判定失敗：{e}")
