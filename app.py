import streamlit as st
import google.generativeai as genai

# 1. 設定頁面
st.set_page_config(page_title="AI 海龜湯防禦系統", page_icon="🐢")

# 2. 獲取 API 金鑰
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("請在 Streamlit Secrets 設定 GEMINI_API_KEY")
    st.stop()

# 3. 基礎初始化（移除所有導致 TypeError 的額外參數）
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def call_gemini_api(prompt_text):
    response = model.generate_content(prompt_text)
    return response.text

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
    
    # 顯示對話與輸入
    for chat in st.session_state.chat_history:
        with st.chat_message(chat["role"]):
            st.write(chat["content"])

    if user_input := st.chat_input("請輸入提問..."):
        with st.chat_message("user"):
            st.write(user_input)
        
        # 建立上下文
        defense_prompt = f"謎底是：{st.session_state.target_answer}。只能回答「是」、「不是」、「與故事/題目無關」或「不完全是」。玩家提問：{user_input}"
        
        with st.chat_message("assistant"):
            try:
                res = call_gemini_api(defense_prompt).strip()
                st.write(res)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": res})
            except Exception as e:
                st.error(f"判定失敗：{e}")
