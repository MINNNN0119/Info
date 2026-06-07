import streamlit as st
import requests
import json
import time

# ==================== 1. 初始化與頁面設定 ====================
st.set_page_config(page_title="AI 海龜湯防禦系統", page_icon="🐢", layout="centered")

# 從後台 Secrets 讀取秘密金鑰
if "GEMINI_API_KEY" in st.secrets:
    api_key_val = st.secrets["GEMINI_API_KEY"]
else:
    st.error("🔑 請先在 Streamlit 進階設定的 Secrets 中設定 `GEMINI_API_KEY`！")
    st.stop()

# ==================== 原生 HTTP 直連函式 (修正為 v1 正式版 API 端點) ====================
def call_gemini_api(prompt_text):
    # 核心修正：將網址明確指定為 /v1/ 正式版路由，並以 query string 帶入 API Key
    # 這樣可以徹底避開 SDK 預設走 v1beta 導致的 404 錯誤，也避免了 Header 認證不支援的 401 錯誤
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key_val}"
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    # 發送 POST 請求
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        res_json = response.json()
        return res_json['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"API 呼召失敗，狀態碼 {response.status_code}: {response.text}")

# ==================== 2. 遊戲核心狀態初始化 ====================
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.target_answer = ""    # 秘密謎底
    st.session_state.chat_history = []     # 對話歷程

# ==================== 3. 畫面排版：未開始畫面 ====================
st.title("🐢 AI 海龜湯（情境猜謎）防禦系統")
st.caption("🛡️ 藍軍期末考對抗賽專用版 | 具備提示注入防禦機制")

if not st.session_state.game_started:
    st.subheader("🎯 啟動遊戲與動態生成謎底")
    st.write("點擊下方按鈕，系統將命令 AI 自動秘密生成一個明確定義的主題目標（如特定水果、運動、生活用品等）。")
    
    if st.button("🎲 秘密生成謎底並開始遊戲", use_container_width=True):
        with st.spinner("AI 正在秘密構思謎底..."):
            try:
                setup_prompt = (
                    "請從【特定球類運動】、【特定水果】、【特定生活用品】中，"
                    "隨機秘密挑選一個明確的物品作為『海龜湯謎底』。"
                    "請直接輸出該物品名稱即可，不要有任何多餘的字（例如直接輸出：西瓜）。"
                )
                secret_word = call_gemini_api(setup_prompt).strip().replace("「", "").replace("」", "").replace("答案是：", "")
                
                # 寫入狀態
                st.session_state.target_answer = secret_word
                st.session_state.chat_history = []  # 重置歷史
                st.session_state.game_started = True
                st.rerun()
            except Exception as e:
                st.error(f"謎底生成失敗！錯誤訊息：{e}")

# ==================== 4. 畫面排版：遊戲進行中 (Chat UI) ====================
else:
    # 🎯 核心功能 1：限縮回應範圍提示
    st.info("💡 **遊戲規則**：請利用下方的對話框向 AI 提問。AI 只能回答「是」、「不是」、「與故事/題目無關」或「不完全是」。")
    st.warning(f"🤫 藍軍後台秘密謎底提示：**【 {st.session_state.target_answer} 】**（請絕對不要洩漏給攻擊方）")

    if st.button("🔄 重新生成謎底 (重置遊戲)"):
        st.session_state.game_started = False
        st.session_state.target_answer = ""
        st.session_state.chat_history = []
        st.rerun()

    st.markdown("---")
    st.subheader("💬 猜題對話歷程")

    # 🎨 核心功能 2：對話歷程完整顯示
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    # 🎨 核心功能 2：採用 st.chat_input 語法建構流暢交談式版面
    if user_input := st.chat_input("請輸入您的提問..."):
        
        # 🛡️ 競賽防禦組規則：限制提問字數長度不能超過 50 個字
        if len(user_input) > 50:
            with st.chat_message("user"):
                st.write(user_input)
            with st.chat_message("assistant"):
                st.error("❌ 提問失敗：對抗賽防禦機制限制提問字數不可超過 50 個字！")
            st.stop()

        # 🛡️ 競賽防禦組規則：設定提問延遲 1 秒，有效阻擋 DDOS 攻擊
        time.sleep(1.0)

        # 立即在畫面上顯示玩家最新提問
        with st.chat_message("user"):
            st.write(user_input)

        # 🎯 核心功能 1：上下文記憶包裝
        history_context = ""
        for chat in st.session_state.chat_history
