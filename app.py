import streamlit as st
from db import *
from auth import login_ui

st.set_page_config(layout="wide")

st.title("🧠 プロンプト管理ツール（無料版）")
st.markdown("""
<style>
.stButton>button {
    border-radius: 10px;
    height: 40px;
}

.stTextInput>div>div>input {
    border-radius: 10px;
}

.stTextArea textarea {
    border-radius: 10px;
}

code {
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# -------------------
# ログイン
# -------------------
if "user" not in st.session_state:
    login_ui()
    st.stop()

user_id = st.session_state.user.id

# -------------------
# 状態管理
# -------------------
if "mode" not in st.session_state:
    st.session_state.mode = "list"

if "search_word" not in st.session_state:
    st.session_state.search_word = ""

if "show_fav" not in st.session_state:
    st.session_state.show_fav = False

# -------------------
# 右サイドバー風レイアウト
# -------------------
col_main, col_side = st.columns([3, 1])

# -------------------
# 右側（操作パネル）
# -------------------
with col_side:
    st.subheader("🔍 検索")

    st.session_state.search_word = st.text_input(
        "キーワード",
        value=st.session_state.search_word
    )

    st.session_state.show_fav = st.checkbox(
        "⭐ お気に入りのみ",
        value=st.session_state.show_fav
    )

    st.write("---")

    if st.button("＋ 新規追加"):
        st.session_state.mode = "create"
        st.rerun()
        

# -------------------
# フィルター関数
# -------------------
def filter_prompts(prompts, word, fav_only):

    results = []

    for p in prompts:

        if word:
            if word.lower() not in p["prompt"].lower() and word.lower() not in p["tag"].lower():
                continue

        if fav_only and not p.get("favorite"):
            continue

        results.append(p)

    return results

# -------------------
# 新規作成画面
# -------------------
def show_create():
    with col_main:

        is_edit = st.session_state.edit_id is not None

        st.subheader("✏ 編集" if is_edit else "➕ 新規プロンプト")

        # 編集対象取得
        if is_edit:
            prompts = get_prompts(user_id)
            target = next(p for p in prompts if p["id"] == st.session_state.edit_id)
            default_prompt = target["prompt"]
            default_tag = target["tag"]
        else:
            default_prompt = ""
            default_tag = ""

        prompt = st.text_area("プロンプト", value=default_prompt)
        tag = st.text_input("タグ", value=default_tag)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("保存"):
                if prompt.strip() != "":
                    if is_edit:
                        update_prompt(st.session_state.edit_id, prompt, tag)
                        st.success("更新しました")
                    else:
                        add_prompt(prompt, tag, user_id)
                        st.success("保存しました")

                    st.session_state.mode = "list"
                    st.session_state.edit_id = None
                    st.rerun()

        with col2:
            if st.button("戻る"):
                st.session_state.mode = "list"
                st.session_state.edit_id = None
                st.rerun()

# -------------------
# 一覧画面
# -------------------
def show_list():
    with col_main:

        st.subheader("📚 プロンプト一覧")

        prompts = get_prompts(user_id)

        prompts = filter_prompts(
            prompts,
            st.session_state.search_word,
            st.session_state.show_fav
        )

        if not prompts:
            st.info("データがありません")
            return

        for p in prompts:

            with st.container():

                st.markdown("----")

                st.markdown("""
                <div style="padding:15px; border-radius:10px; background-color:#f9f9f9;">
                """, unsafe_allow_html=True)

                # タグボタン
                tags = [t.strip() for t in p["tag"].split(",")]
                tag_cols = st.columns(len(tags))

                for i, t in enumerate(tags):
                    if tag_cols[i].button(t, key=f"tag_{p['id']}_{i}"):
                        st.session_state.search_word = t
                        st.rerun()

                # 本文
                star = "⭐" if p.get("favorite") else ""
                st.markdown(f"### {star}")
                st.code(p["prompt"])

                # ボタン
                col1, col2, col3 = st.columns(3)

                with col1:
                    if st.button("⭐", key=p["id"]):
                        toggle_favorite(p["id"], p.get("favorite", False))
                        st.rerun()

                with col2:
                    if st.button("✏", key="edit"+p["id"]):
                        st.session_state.edit_id = p["id"]
                        st.session_state.mode = "create"
                        st.rerun()

                with col3:
                    if st.button("削除", key="del"+p["id"]):
                        delete_prompt(p["id"])
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)
                
# -------------------
# 画面切り替え
# -------------------
if st.session_state.mode == "create":
    show_create()
else:
    show_list()