import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="MCQ Practice & Test Tool", layout="centered")

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'used_indexes' not in st.session_state:
    st.session_state.used_indexes = set()
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'mode' not in st.session_state:
    st.session_state.mode = None
if 'question_index' not in st.session_state:
    st.session_state.question_index = 0
if 'test_answers' not in st.session_state:
    st.session_state.test_answers = []

st.title("🧠 MCQ Practice & Test Tool")

# Upload CSV
st.sidebar.header("Upload CSV File")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")

# Load questions from CSV
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'id' not in df.columns:
        df.insert(0, 'id', range(1, len(df) + 1))
    st.session_state.questions = df.to_dict(orient='records')
    st.success(f"Loaded {len(st.session_state.questions)} questions.")

# Function to get next question
def get_next_question():
    remaining = [i for i in range(len(st.session_state.questions)) if i not in st.session_state.used_indexes]
    if not remaining:
        return None, -1
    index = random.choice(remaining)
    st.session_state.used_indexes.add(index)
    return st.session_state.questions[index], index

# Function to show result
def show_result():
    st.subheader("✅ Test Completed")
    total = len(st.session_state.test_answers)
    score = st.session_state.score
    passing_score = 0.6 * total
    result = "PASS" if score >= passing_score else "FAIL"
    st.markdown(f"**Your Score:** {score:.2f} / {total}")
    st.markdown(f"**Result:** {result}")

    wrongs = [q for q in st.session_state.test_answers if q['your_answer'] != q['correct']]
    if wrongs:
        st.download_button("📥 Download Wrong Answers", data='\n'.join([f"Q: {q['question']} | Your: {q['your_answer']} | Correct: {q['correct']}" for q in wrongs]), file_name="wrong_answers.txt")

    if st.button("🔁 Back to Menu"):
        for key in st.session_state:
            st.session_state[key] = None
        st.experimental_rerun()

# Main Menu
if not st.session_state.mode:
    st.subheader("Select Mode")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Practice Mode"):
            st.session_state.mode = "practice"
    with col2:
        if st.button("🧪 Test Mode (50 Questions)"):
            st.session_state.mode = "test"
            st.session_state.score = 0
            st.session_state.test_answers = []
            st.session_state.used_indexes = set()

# PRACTICE MODE
if st.session_state.mode == "practice":
    question, idx = get_next_question()
    if question:
        st.markdown(f"**Q{idx+1}: {question['question']}**")
        options = ['a', 'b', 'c', 'd']
        choice = st.radio("Choose your answer:", options, format_func=lambda x: f"{x.upper()}) {question[f'option_{x}']}")
        if st.button("Submit Answer"):
            if choice == question['correct_option']:
                st.success("✅ Correct Answer!")
            else:
                st.error(f"❌ Wrong. Correct Answer is {question['correct_option'].upper()}")
            if st.button("Next Question"):
                st.experimental_rerun()
    else:
        st.info("All questions completed.")
        if st.button("Back to Menu"):
            for key in st.session_state:
                st.session_state[key] = None
            st.experimental_rerun()

# TEST MODE
if st.session_state.mode == "test":
    if len(st.session_state.test_answers) >= 50:
        show_result()
    else:
        question, idx = get_next_question()
        if question:
            st.markdown(f"**Q{len(st.session_state.test_answers)+1}: {question['question']}**")
            options = ['a', 'b', 'c', 'd']
            choice = st.radio("Choose your answer:", options, format_func=lambda x: f"{x.upper()}) {question[f'option_{x}']}", key=f"test_q_{idx}")
            if st.button("Submit Answer"):
                correct = question['correct_option']
                st.session_state.test_answers.append({
                    'question': question['question'],
                    'your_answer': choice,
                    'correct': correct
                })
                if choice == correct:
                    st.session_state.score += 1
                else:
                    st.session_state.score -= 0.25
                st.experimental_rerun()
        else:
            st.info("No more questions available.")
            show_result()
