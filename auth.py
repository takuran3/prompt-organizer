import streamlit as st
from supabase import create_client

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def login_ui():

    email = st.text_input("メール")
    password = st.text_input("パスワード", type="password")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("ログイン"):
            try:
                res = supabase.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })

                if res.user:
                    st.session_state.user = res.user
                    st.success("ログイン成功")
                    st.rerun()
                else:
                    st.error("ログイン失敗")

            except Exception as e:
                st.error(f"エラー: {e}")

    with col2:
        if st.button("新規登録"):
            try:
                supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                st.success("登録成功")
            except:
                st.error("登録失敗")