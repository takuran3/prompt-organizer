from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_embedding(text):
    try:
        res = client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return res.data[0].embedding
    except Exception as e:
        print(e)
        return None

# def run_ai(prompt, model="gpt-4o-mini"):
#     try:
#         res = client.chat.completions.create(
#             model=model,
#             messages=[{"role": "user", "content": prompt}]
#         )
#         return res.choices[0].message.content
#     except Exception as e:
#         return f"AIエラー: {e}"


# def generate_tags(prompt):
#     try:
#         res = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{
#                 "role": "user",
#                 "content": f"""
# 次のプロンプトに合うタグを3〜5個
# カンマ区切りで出力してください。

# {prompt}
# """
#             }]
#         )
#         return res.choices[0].message.content
#     except:
#         return ""


# def improve_prompt(prompt):
#     try:
#         res = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{
#                 "role": "user",
#                 "content": f"""
# 次のプロンプトを改善してください

# {prompt}
# """
#             }]
#         )
#         return res.choices[0].message.content
#     except:
#         return prompt


# def evaluate_prompt(prompt):
#     try:
#         res = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{
#                 "role": "user",
#                 "content": f"""
# このプロンプトを10点満点で評価し改善点も教えてください

# {prompt}
# """
#             }]
#         )
#         return res.choices[0].message.content
#     except:
#         return ""


# def generate_prompt(topic):
#     try:
#         res = client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=[{
#                 "role": "user",
#                 "content": f"{topic}に使えるプロンプトを10個作ってください"
#             }]
#         )
#         return res.choices[0].message.content.split("\n")
#     except:
#         return []


    