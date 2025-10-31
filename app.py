import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="Learnify", page_icon="💻", layout="wide")

# CSV file name
CSV_FILE = "quiz_questions.csv"

# Load CSV data
@st.cache_data
def load_questions():
    df = pd.read_csv(CSV_FILE)
    return df

df = load_questions()

# UI
st.title("Techify - Quiz Your Inner Geek!")
st.markdown("<h5 style='color:gray;'>Test your computer and technology knowledge!</h5>", unsafe_allow_html=True)
st.divider()

# Sidebar for navigation
menu = st.sidebar.radio("📚 Menu", ["Take Quiz", "Add Question"])

# ------------------------ QUIZ MODE ------------------------
if menu == "Take Quiz":
    st.subheader("🧠 Take the Quiz")
    score = 0
    total = len(df)

    for index, row in df.iterrows():
        q_type = row["type"]
        question = row["question"]
        options = json.loads(row["options"])
        answer = str(row["answer"]).strip()

        st.write(f"**Q{index + 1}. {question}**")

        if q_type == "Multiple Choice":
            user_answer = st.radio("", list(options.values()), key=index)
            correct_option = options.get(answer, "")
            if user_answer == correct_option:
                score += 1

        elif q_type == "True or False":
            user_answer = st.radio("", ["True", "False"], key=index)
            if user_answer.lower() == answer.lower():
                score += 1

        elif q_type == "Fill in the Blank":
            user_answer = st.text_input("", key=index)
            if user_answer.strip().lower() == answer.lower():
                score += 1

        st.markdown("---")

    if st.button("✅ Submit Quiz"):
        st.success(f"Your Score: {score}/{total}")
        st.balloons()

# ------------------------ ADD QUESTION MODE ------------------------
elif menu == "Add Question":
    st.subheader("➕ Add a New Question")

    q_type = st.selectbox("Question Type", ["Multiple Choice", "True or False", "Fill in the Blank"])
    question = st.text_area("Enter Question")

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

    else:  # Fill in the Blank
        options = json.dumps({})
        answer = st.text_input("Correct Answer")

    if st.button("💾 Save Question"):
        new_data = pd.DataFrame([[q_type, question, options, answer]], columns=df.columns)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("✅ Question added successfully!")