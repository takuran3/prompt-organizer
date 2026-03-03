import streamlit as st
import json
import os

FILE_NAME = "prompts.json"

def load_prompts():
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_prompts(prompts):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

st.title("プロンプト整理ツール")
st.markdown("## ➕ 新規追加")

prompt = st.text_area("プロンプトを入力")
tag = st.text_input("タグ")

if st.button("保存"):
    if prompt.strip() == "":
        st.warning("プロンプトを入力してください")
    else:
        prompts = load_prompts()
        prompts.append({"prompt": prompt, "tag": tag})
        save_prompts(prompts)
        st.success("保存しました")
        st.rerun()

st.subheader("保存済みプロンプト")
st.markdown("## 🔍 検索")

search_word = st.text_input("タグ、プロンプトで検索")

prompts = load_prompts()
search_word = search_word.lower()

prompts = list(reversed(prompts))

for i, p in enumerate(prompts):
    if (
        search_word == ""
        or search_word in p["tag"].lower()
        or search_word in p["prompt"].lower()
    ):
        with st.container():
             st.markdown(f"### 🏷 {p['tag']}")
             st.write(p["prompt"])
        
        if st.button("削除", key=i):
            prompts.pop(i)
            save_prompts(prompts)
            st.rerun()

        st.write("---")
