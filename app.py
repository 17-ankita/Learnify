import streamlit as st
import pandas as pd
import json
import requests
from datetime import datetime

# -------------------- CONFIG --------------------
st.set_page_config(page_title="💻 Learnify", page_icon="💡", layout="wide")

BACKEND_URL = "http://10.0.3.33:5000"  # Replace with your backend URL
CSV_FILE = "quiz.csv"
LEADERBOARD_FILE = "leaderboard.csv"

# -------------------- LOAD QUESTIONS --------------------
@st.cache_data
def load_questions():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["type", "question", "options", "answer"])

# -------------------- LOAD LEADERBOARD --------------------
def load_leaderboard():
    try:
        return pd.read_csv(LEADERBOARD_FILE)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Name", "Email", "Score", "Date"])

def save_to_leaderboard(name, email, score):
    df = load_leaderboard()
    new_row = pd.DataFrame({
        "Name": [name],
        "Email": [email],
        "Score": [score],
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(LEADERBOARD_FILE, index=False)

# -------------------- SESSION STATE --------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "name" not in st.session_state:
    st.session_state.name = ""
if "email" not in st.session_state:
    st.session_state.email = ""

# -------------------- LOGIN PAGE --------------------
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align:center;'>🔐 Welcome to Learnify!</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray;'>Please log in to continue.</p>", unsafe_allow_html=True)

    # Centered & narrower login form
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        name = st.text_input("👤 Name", placeholder="Enter your name")
        email = st.text_input("📧 Email", placeholder="Enter your email")

        if st.button("Login", use_container_width=True):
            if name and email:
                st.session_state.logged_in = True
                st.session_state.name = name
                st.session_state.email = email
                st.rerun()
            else:
                st.warning("Please enter both name and email to continue.")

    st.stop()

# -------------------- MAIN APP --------------------
df = load_questions()

st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Choose an option", ["Take Quiz", "Add Question", "Leaderboard", "Logout"])

# -------------------- TAKE QUIZ --------------------
if menu == "Take Quiz":
    st.header("🧠 Take the Quiz")
    if df.empty:
        st.warning("No quiz questions available yet.")
    else:
        total = len(df)
        score = 0
        user_answers = {}

        for i, row in df.iterrows():
            q_type = row["type"]
            question = row["question"]
            options = json.loads(row["options"])
            answer = str(row["answer"]).strip()

            st.write(f"**Q{i + 1}. {question}**")

            if q_type == "Multiple Choice":
                user_answers[i] = st.radio("", list(options.values()), key=i)
                correct_option = options.get(answer, "")
                if user_answers[i] == correct_option:
                    score += 1

            elif q_type == "True or False":
                user_answers[i] = st.radio("", ["True", "False"], key=i)
                if user_answers[i].lower() == answer.lower():
                    score += 1

            elif q_type == "Fill in the Blank":
                user_answers[i] = st.text_input("", key=i)
                if user_answers[i].strip().lower() == answer.lower():
                    score += 1

            st.markdown("---")

        if st.button("✅ Submit Quiz"):
            st.success(f"Your Score: {score}/{total}")
            st.balloons()
            save_to_leaderboard(st.session_state.name, st.session_state.email, score)

# -------------------- ADD QUESTION --------------------
elif menu == "Add Question":
    st.header("➕ Add a New Question")

    q_type = st.selectbox("Question Type", ["Multiple Choice", "True or False", "Fill in the Blank"])
    question = st.text_area("Enter Question")

    opt_a = opt_b = opt_c = opt_d = ""
    answer = ""

    if q_type == "Multiple Choice":
        opt_a = st.text_input("Option A")
        opt_b = st.text_input("Option B")
        opt_c = st.text_input("Option C")
        opt_d = st.text_input("Option D")
        answer = st.selectbox("Correct Answer", ["A", "B", "C", "D"])
        options = json.dumps({"A": opt_a, "B": opt_b, "C": opt_c, "D": opt_d})

    elif q_type == "True or False":
        options = json.dumps({"A": "True", "B": "False"})
        answer = st.selectbox("Correct Answer", ["True", "False"])

    else:
        options = json.dumps({})
        answer = st.text_input("Correct Answer")

    if st.button("💾 Save Question"):
        new_question = {
            "type": q_type,
            "question": question,
            "options": options,
            "answer": answer
        }

        try:
            response = requests.post(f"{BACKEND_URL}/save-quiz", json=[new_question])
            if response.status_code == 200:
                st.success("✅ Question saved successfully!")
            else:
                st.error(f"❌ Failed to save: {response.text}")
        except Exception as e:
            st.error(f"⚠️ Could not connect to backend: {e}")

# -------------------- LEADERBOARD --------------------
elif menu == "Leaderboard":
    st.header("🏆 Leaderboard")
    leaderboard = load_leaderboard()

    if leaderboard.empty:
        st.info("No scores yet. Be the first to take the quiz!")
    else:
        leaderboard = leaderboard.sort_values(by="Score", ascending=False).reset_index(drop=True)
        st.dataframe(leaderboard)

# -------------------- LOGOUT --------------------
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.name = ""
    st.session_state.email = ""
    st.success("You’ve been logged out.")
    st.rerun()
