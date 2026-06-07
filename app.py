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

# ==================== 原生 HTTP 直連函式 (修正 AQ. 金鑰之 Bearer 認證機制) ====================
def call_gemini_api(prompt_text):
    # 1. 使用不帶 key= 參數的標準模型 URL 端點，強迫對齊正式版路由
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    
    # 2. 將 AQ. 金鑰包裝在 Authorization 標頭中，符合 OAuth 2 / 服務帳戶認證規範
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key_val}'
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": prompt_text}]
        }]
    }
    
    # 3. 發送 POST 請求
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        res_json = response.json()
        return res_json['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"API 呼叫失敗，狀態碼 {response.status_code}: {response.text}")

# ==================== 2. 遊戲核心狀態初始化 ====================
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.target_answer = ""    # 秘密謎底
    st.session_state.chat_history = []     # 對話歷程 (包含歷史紀錄包裝)

# ==================== 3. 畫面排版：未開始畫面 ====================
st.title("🐢 AI 海龜湯（情境猜謎）防禦系統")
st.caption("🛡️ 藍軍期末考對抗賽專用版 | 具備提示注入防禦機制")

if not st.session_state.game_started:
    st.subheader("🎯 啟動遊戲與動態生成謎底")
    st.write("點擊下方按鈕，系統將命令 AI 自動秘密生成一個明確定義的主題
