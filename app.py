import streamlit as st
import uuid
import json
import os

FILE_NAME = "prompts.json"


def load_prompts():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            st.error("JSONファイルが壊れています")
            return []
    return []


def save_prompts(prompts):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)


st.title("🧠 プロンプト整理ツール")

prompts = load_prompts()

# -------------------
# タグ収集
# -------------------

all_tags = []
for p in prompts:
    all_tags.extend([t.strip() for t in p["tag"].split(",") if t.strip() != ""])

unique_tags = sorted(set(all_tags))

# -------------------
# メトリクス
# -------------------

col1, col2 = st.columns(2)

col1.metric("プロンプト数", len(prompts))
col2.metric("タグ数", len(unique_tags))

# -------------------
# 状態管理
# -------------------

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if "tag_filter" not in st.session_state:
    st.session_state.tag_filter = ""

# -------------------
# 新規追加 / 編集
# -------------------

st.markdown("## ➕ 新規追加 / 編集")

edit_index = st.session_state.edit_index

if edit_index is not None:
    default_prompt = prompts[edit_index]["prompt"]
    default_tag = prompts[edit_index]["tag"]
else:
    default_prompt = ""
    default_tag = ""

prompt = st.text_area("プロンプト", value=default_prompt)
tag = st.text_input("タグ（カンマ区切り）", value=default_tag, key="tag_input")

st.caption("タグ候補")

tag_cols = st.columns(6)

for i, t in enumerate(unique_tags):
    if tag_cols[i % 6].button(t, key=f"suggest_{t}"):
        if st.session_state.tag_input == "":
            st.session_state.tag_input = t
        else:
            st.session_state.tag_input += "," + t
        st.rerun()

if st.button("保存"):
    if prompt.strip() == "":
        st.warning("プロンプトを入力してください")

    else:
        if edit_index is not None:

            prompts[edit_index]["prompt"] = prompt
            prompts[edit_index]["tag"] = tag

            st.session_state.edit_index = None

        else:

            prompts.append(
                {
                    "id": str(uuid.uuid4()),
                    "prompt": prompt,
                    "tag": tag,
                    "favorite": False,
                }
            )

        save_prompts(prompts)
        st.success("保存しました")
        st.rerun()

# -------------------
# 検索
# -------------------

st.markdown("## 🔍 検索")

sort_mode = st.selectbox(
    "並び替え",
    ["新しい順", "古い順", "お気に入り優先"],
)

show_favorites = st.checkbox("⭐ お気に入りのみ")

search_word = st.text_input(
    "タグ / プロンプト検索",
    value=st.session_state.tag_filter,
)

search_word = search_word.lower()

# -------------------
# 並び替え
# -------------------

if sort_mode == "新しい順":
    display_prompts = list(reversed(prompts))

elif sort_mode == "古い順":
    display_prompts = prompts

elif sort_mode == "お気に入り優先":
    display_prompts = sorted(
        prompts,
        key=lambda x: x.get("favorite", False),
        reverse=True,
    )

# -------------------
# タグ一覧
# -------------------

st.markdown("### 🏷 タグ一覧")

tag_cols = st.columns(6)

for i, tag_name in enumerate(unique_tags):
    if tag_cols[i % 6].button(tag_name, key=f"tag_{tag_name}"):
        st.session_state.tag_filter = tag_name
        st.rerun()

if st.button("フィルター解除"):
    st.session_state.tag_filter = ""
    st.rerun()

# -------------------
# プロンプト表示
# -------------------

st.markdown("## 📚 保存済みプロンプト")

for i, p in enumerate(display_prompts):

    tag_match = search_word in p["tag"].lower()
    text_match = search_word in p["prompt"].lower()

    search_match = search_word == "" or tag_match or text_match

    favorite_match = not show_favorites or p.get("favorite", False)

    if search_match and favorite_match:

        with st.container():

            tags = [t.strip() for t in p["tag"].split(",") if t.strip()]

            tag_text = " ".join([f"`{t}`" for t in tags])

            star = "⭐" if p.get("favorite") else ""

            st.markdown(f"### {star} 🏷 {tag_text}")

            st.code(p["prompt"])

            col1, col2, col3 = st.columns(3)

            with col1:

                if st.button("✏ 編集", key=f"edit_{p['id']}"):

                    for idx, item in enumerate(prompts):
                        if item["id"] == p["id"]:
                            st.session_state.edit_index = idx
                            break

                    st.rerun()

            with col2:

                if st.button("🗑 削除", key=f"delete_{p['id']}"):

                    prompts = [x for x in prompts if x["id"] != p["id"]]

                    save_prompts(prompts)

                    st.rerun()

            with col3:

                if st.button("⭐", key=f"fav_{p['id']}"):

                    for item in prompts:
                        if item["id"] == p["id"]:
                            item["favorite"] = not item.get("favorite", False)

                    save_prompts(prompts)

                    st.rerun()

        st.write("---")