import streamlit as st
import google.generativeai as genai

# ==================== 1. 初始化與 API 設定 ====================
st.set_page_config(page_title="AI 海龜湯（情境猜謎）系統", page_icon="🐢", layout="centered")

# 優先讀取 Streamlit Secrets 的設定
if "GEMINI_API_KEY" in st.secrets:
    api_key_val = st.secrets["GEMINI_API_KEY"]
elif "api_key" in st.secrets:
    api_key_val = st.secrets["api_key"]
else:
    st.error("🔑 請先在 Streamlit 後台設定 `GEMINI_API_KEY`！")
    st.stop()

# 核心修正：使用標準金鑰配置方式
try:
    genai.configure(api_key=api_key_val)
except Exception as e:
    st.error(f"金鑰配置失敗：{e}")
    st.stop()

# 初始化 session_state，用來記錄遊戲狀態
if "game_started" not in st.session_state:
    st.session_state.game_started = False
    st.session_state.title = ""
    st.session_state.question = ""
    st.session_state.truth = ""
    if "history" not in st.session_state:
        st.session_state.history = []

# ==================== 2. 遊戲介面與邏輯 ====================
st.title("🐢 AI 海龜湯（情境猜謎）系統")
st.write("這是一個需要由你提問、AI 來回答『是/不是/與此無關』的情境推理遊戲。")

# 狀況 A：遊戲尚未開始 -> 顯示輸入湯底的界面
if not st.session_state.game_started:
    st.subheader("📝 設定你的海龜湯題目")
    
    with st.form("setup_form"):
        title_input = st.text_input("1. 題目名稱（例如：半根火柴）", placeholder="請輸入有趣的標題...")
        question_input = st.text_area("2. 湯面（讓玩家看的情境描述）", placeholder="例如：一個男人躺在沙漠中死去了，手裡握著半根火柴。請問發生了什麼事？")
        truth_input = st.text_area("3. 湯底（只有 AI 知道的真實故事答案）", placeholder="例如：他們搭乘的熱氣球超重了，大家抽火柴決定誰要被丟下去...")
        
        submit_btn = st.form_submit_button("開始遊戲！")
        
        if submit_btn:
            if title_input and question_input and truth_input:
                st.session_state.title = title_input
                st.session_state.question = question_input
                st.session_state.truth = truth_input
                st.session_state.game_started = True
                st.session_state.history = []  # 清空先前的對話紀錄
                st.rerun()
            else:
                st.warning("⚠️ 請填寫所有欄位再開始遊戲！")

# 狀況 B：遊戲進行中 -> 玩家提問界面
else:
    st.header(f"📌 當前挑戰：{st.session_state.title}")
    
    # 顯示湯面（情境描述）
    st.info(f"**【湯面】**\n\n{st.session_state.question}")
    
    # 提供一個按鈕可以重置遊戲
    if st.button("🔄 重置並更換題目"):
        st.session_state.game_started = False
        st.rerun()

    st.markdown("---")
    st.subheader("💬 向 AI 提問")
    
    # 玩家輸入框
    user_query = st.text_input("請輸入你的問題（提示：必須是能用『是/不是』回答的封閉式問題）：", key="user_query_input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ask_btn = st.button("❓ 提問", use_container_width=True)
    with col2:
        guess_btn = st.button("🎯 我要猜真相（直接對答案）", use_container_width=True)

    # 處理提問邏輯
    if ask_btn and user_query:
        with st.spinner("AI 正在思考判定中..."):
            try:
                # 採用通用穩定的模型版本
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                你現在是一個嚴格的海龜湯（情境推理遊戲）裁判。
                
                【湯面（公開情境）】：{st.session_state.question}
                【湯底（真實解答）】：{st.session_state.truth}
                
                現在玩家問了這個問題：『{user_query}』
                
                請你根據【湯底】的真相，判斷玩家的問題。
                你『只能』從以下四個標準回答中選擇一個回答，絕對不能說多餘的話，也不能透露任何真相細節：
                1. 是。
                2. 不是。
                3. 與此無關。
                4. 請嘗試用能以「是/不是」回答的方式重新提問。
                """
                
                response = model.generate_content(prompt)
                ai_answer = response.text.strip()
                
                st.session_state.history.insert(0, {"query": user_query, "answer": ai_answer, "type": "ask"})
            except Exception as e:
                st.error(f"連線或認證失敗：{e}。請檢查金鑰是否複製完整。")

    # 處理猜測真相邏輯
    elif guess_btn and user_query:
        with st.spinner("AI 正在評估你是否接近真相..."):
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                prompt = f"""
                你現在是海龜湯裁判。
                【湯底（真實解答）】：{st.session_state.truth}
                
                玩家試圖猜出完整真相，他的答案是：『{user_query}』
                
                請評估玩家是否已經掌握了核心真相。
                如果已經完全答對或非常接近核心事實，請回答：『🎉 恭喜你！成功破案！答案就是：(後面加上你對湯底的精簡總結)』
                如果還差得遠或完全不對，請回答：『❌ 很遺憾，這並不是事情的真相，再接再厲！』
                """
                
                response = model.generate_content(prompt)
                ai_answer = response.text.strip()
                
                st.session_state.history.insert(0, {"query": user_query, "answer": ai_answer, "type": "guess"})
            except Exception as e:
                st.error(f"連線或認證失敗：{e}")

    # ==================== 3. 顯示歷史問答紀錄 ====================
    if st.session_state.history:
        st.markdown("### 📜 提問紀錄")
        for idx, item in enumerate(st.session_state.history):
            if item["type"] == "guess":
                st.markdown(f"**🧐 猜測：** {item['query']}")
                st.markdown(f"**📢 判定：** {item['answer']}")
            else:
                st.markdown(f"**🙋 問：** {item['query']}  ➡️  **🤖 答：** `{item['answer']}`")
            st.markdown("---")
