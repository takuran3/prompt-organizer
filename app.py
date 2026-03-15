import streamlit as st
from openai import OpenAI
import uuid
import json
import os
import pandas as pd
from datetime import datetime

client = OpenAI()

FILE_NAME = "prompts.json"
HISTORY_FILE = "history.json"

# -----------------------------
# ファイル読み込み
# -----------------------------

def load_json(file):

    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []

    return []


def save_json(file, data):

    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# -----------------------------
# AI実行
# -----------------------------

def run_ai(prompt):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


# -----------------------------
# AIタグ生成
# -----------------------------

def generate_tags(prompt):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"""
次のプロンプトに合うタグを
3〜5個作ってください。

カンマ区切りで出力してください。

{prompt}
"""
            }
        ]
    )

    return response.choices[0].message.content


# -----------------------------
# プロンプト改善
# -----------------------------

def improve_prompt(prompt):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"""
次のプロンプトを

・より明確に
・AIが答えやすく
・高品質な回答が出るように

改善してください。

{prompt}
"""
            }
        ]
    )

    return response.choices[0].message.content


# -----------------------------
# データ読み込み
# -----------------------------

prompts = load_json(FILE_NAME)
history = load_json(HISTORY_FILE)

# -----------------------------
# タイトル
# -----------------------------

st.title("🧠 AIプロンプト管理ツール")

# -----------------------------
# タグ収集
# -----------------------------

all_tags = []

for p in prompts:
    tags = [t.strip() for t in p["tag"].split(",") if t.strip()]
    all_tags.extend(tags)

unique_tags = sorted(set(all_tags))

# -----------------------------
# タグ分析
# -----------------------------

if all_tags:
    df = pd.DataFrame(all_tags, columns=["tag"])
    tag_count = df["tag"].value_counts()
else:
    tag_count = pd.Series()

# -----------------------------
# メトリクス
# -----------------------------

col1, col2, col3 = st.columns(3)

col1.metric("プロンプト数", len(prompts))
col2.metric("タグ数", len(unique_tags))
col3.metric("AI履歴", len(history))

# -----------------------------
# 状態管理
# -----------------------------

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if "tag_filter" not in st.session_state:
    st.session_state.tag_filter = ""

# -----------------------------
# 新規追加 / 編集
# -----------------------------

st.markdown("## ➕ プロンプト追加 / 編集")

edit_index = st.session_state.edit_index

if edit_index is not None:
    default_prompt = prompts[edit_index]["prompt"]
    default_tag = prompts[edit_index]["tag"]
else:
    default_prompt = ""
    default_tag = ""

prompt = st.text_area("プロンプト", value=default_prompt)
tag = st.text_input("タグ（カンマ区切り）", value=default_tag, key="tag_input")

# -----------------------------
# AIボタン
# -----------------------------

col1, col2 = st.columns(2)

with col1:

    if st.button("🧠 AIタグ生成"):

        if prompt.strip() != "":
            tags = generate_tags(prompt)
            st.session_state.tag_input = tags
            st.rerun()

with col2:

    if st.button("✨ プロンプト改善"):

        if prompt.strip() != "":

            with st.spinner("AI改善中..."):

                improved = improve_prompt(prompt)

            prompt = improved
            st.success("改善しました")

# -----------------------------
# タググラフ
# -----------------------------

if len(tag_count) > 0:

    st.bar_chart(tag_count)

st.caption("タグ候補")

# -----------------------------
# タグ候補ボタン
# -----------------------------

tag_cols = st.columns(6)

for i, t in enumerate(unique_tags):

    if tag_cols[i % 6].button(t, key=f"suggest_{t}"):

        if st.session_state.tag_input == "":
            st.session_state.tag_input = t
        else:
            st.session_state.tag_input += "," + t

        st.rerun()

# -----------------------------
# 保存
# -----------------------------

if st.button("💾 保存"):

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

        save_json(FILE_NAME, prompts)

        st.success("保存しました")

        st.rerun()

# -----------------------------
# 検索
# -----------------------------

st.markdown("## 🔍 検索")

sort_mode = st.selectbox(
    "並び替え",
    ["新しい順", "古い順", "お気に入り優先"]
)

show_favorites = st.checkbox("⭐ お気に入りのみ")

search_word = st.text_input(
    "タグ / プロンプト検索",
    value=st.session_state.tag_filter
)

search_word = search_word.lower()

# -----------------------------
# 並び替え
# -----------------------------

if sort_mode == "新しい順":

    display_prompts = list(reversed(prompts))

elif sort_mode == "古い順":

    display_prompts = prompts

else:

    display_prompts = sorted(
        prompts,
        key=lambda x: x.get("favorite", False),
        reverse=True
    )

# -----------------------------
# タグ一覧
# -----------------------------

st.markdown("### 🏷 タグ一覧")

tag_cols = st.columns(6)

for i, tag_name in enumerate(unique_tags):

    if tag_cols[i % 6].button(tag_name, key=f"tag_{tag_name}"):

        st.session_state.tag_filter = tag_name
        st.rerun()

if st.button("フィルター解除"):

    st.session_state.tag_filter = ""
    st.rerun()

# -----------------------------
# プロンプト表示
# -----------------------------

st.markdown("## 📚 保存済みプロンプト")

for p in display_prompts:

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

            col1, col2, col3, col4 = st.columns(4)

            # AI実行
            with col1:

                if st.button("🤖 AI実行", key=f"run_{p['id']}"):

                    with st.spinner("AI考え中..."):

                        result = run_ai(p["prompt"])

                    st.markdown("#### 🤖 AI回答")
                    st.write(result)

                    history.append(
                        {
                            "prompt": p["prompt"],
                            "result": result,
                            "time": str(datetime.now())
                        }
                    )

                    save_json(HISTORY_FILE, history)

            # 編集
            with col2:

                if st.button("✏ 編集", key=f"edit_{p['id']}"):

                    for idx, item in enumerate(prompts):

                        if item["id"] == p["id"]:
                            st.session_state.edit_index = idx
                            break

                    st.rerun()

            # 削除
            with col3:

                if st.button("🗑 削除", key=f"delete_{p['id']}"):

                    prompts = [x for x in prompts if x["id"] != p["id"]]

                    save_json(FILE_NAME, prompts)

                    st.rerun()

            # お気に入り
            with col4:

                if st.button("⭐", key=f"fav_{p['id']}"):

                    for item in prompts:

                        if item["id"] == p["id"]:
                            item["favorite"] = not item.get("favorite", False)

                    save_json(FILE_NAME, prompts)

                    st.rerun()

        st.write("---")

# -----------------------------
# AI履歴
# -----------------------------

st.markdown("## 📜 AI回答履歴")

for h in reversed(history[-10:]):

    with st.container():

        st.caption(h["time"])

        st.markdown("**Prompt**")
        st.code(h["prompt"])

        st.markdown("**Result**")
        st.write(h["result"])

        st.write("---")

if st.button("履歴削除"):

    history = []
    save_json(HISTORY_FILE, history)

    st.rerun()