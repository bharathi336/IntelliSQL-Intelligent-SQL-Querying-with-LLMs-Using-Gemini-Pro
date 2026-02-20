import os
import sqlite3
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai

# -------------------- ENV & GEMINI SETUP --------------------
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in .env file")
    st.stop()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
# -------------------- PROMPT --------------------
PROMPT = """
You are an expert in converting English questions to SQL queries.

The SQLite database has ONE table named Students with the following columns:
name, class, marks, company

Rules:
- Only generate valid SQLite SQL
- Do NOT explain anything
- Do NOT add markdown
- Return ONLY the SQL query

Examples:

Question: How many entries are present?
SQL: SELECT COUNT(*) FROM Students;

Question: Tell me all the students studying in MCom class?
SQL: SELECT * FROM Students WHERE class='MCom';
"""

# -------------------- GEMINI → SQL --------------------
def get_sql_query(question: str) -> str:
    response = model.generate_content(PROMPT + "\nQuestion: " + question)
    sql = response.text.strip()

    # Safety cleanup
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

# -------------------- DATABASE EXECUTION --------------------
def execute_sql(sql: str, db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.close()
    return rows

# -------------------- PAGES --------------------
def page_home():
    st.markdown("""
        <style>
            body { background-color: #2E2E2E; }
            .title { text-align:center; color:#4CAF50; font-size:40px; }
            .subtitle { text-align:center; color:#4CAF50; font-size:22px; }
            .text { color:white; font-size:18px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='title'>Welcome to IntelliSQL</div>", unsafe_allow_html=True)
    st.markdown("<div class='subtitle'>Query Databases Using Natural Language</div>", unsafe_allow_html=True)

    st.image(
        "https://cdn1.iconfinder.com/data/icons/business-dual-color-glyph-set-3/128/Data_warehouse-1024.png",
        width=300
    )

def page_about():
    st.markdown("""
        <style>
            .content { color:white; font-size:18px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='color:#4CAF50;'>About IntelliSQL</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div class='content'>
        IntelliSQL allows users to query SQL databases using plain English.
        It leverages Google's Gemini LLM to convert natural language into SQL.
        </div>
    """, unsafe_allow_html=True)

def page_query():
    st.markdown("<h1 style='color:#4CAF50;'>Intelligent Query Assistance</h1>", unsafe_allow_html=True)

    question = st.text_input("Enter your question in English:")
    submit = st.button("Generate & Execute SQL")

    if submit and question:
        try:
            sql = get_sql_query(question)
            st.success("Generated SQL:")
            st.code(sql, language="sql")

            results = execute_sql(sql, "data.db")
            st.subheader("Query Result:")
            st.table(results)

        except Exception as e:
            st.error(f"❌ Error: {e}")

# -------------------- MAIN --------------------
def main():
    st.set_page_config(
        page_title="IntelliSQL",
        page_icon="🌟",
        layout="wide"
    )

    st.sidebar.title("Navigation")
    choice = st.sidebar.radio(
        "Go to",
        ["Home", "About", "Intelligent Query Assistance"]
    )

    if choice == "Home":
        page_home()
    elif choice == "About":
        page_about()
    else:
        page_query()

if __name__ == "__main__":
    main()