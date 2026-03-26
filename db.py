from supabase import create_client
import streamlit as st

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

def get_prompts(user_id):
    res = supabase.table("prompts") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()
    return res.data


def add_prompt(prompt, tag, user_id):
    supabase.table("prompts").insert({
        "prompt": prompt,
        "tag": tag,
        "user_id": user_id,
        "favorite": False
    }).execute()


def delete_prompt(pid):
    supabase.table("prompts") \
        .delete() \
        .eq("id", pid) \
        .execute()


def toggle_favorite(pid, current):
    supabase.table("prompts") \
        .update({"favorite": not current}) \
        .eq("id", pid) \
        .execute()
        
def update_prompt(pid, prompt, tag):
    supabase.table("prompts") \
        .update({
            "prompt": prompt,
            "tag": tag
        }) \
        .eq("id", pid) \
        .execute()