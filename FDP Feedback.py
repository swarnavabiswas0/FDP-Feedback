import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import pytz
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt

# ---------- Google Sheets Auth ----------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_key = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
client = gspread.authorize(creds)

# ---------- Open Sheet ----------
sheet_url = "https://docs.google.com/spreadsheets/d/1FyNxVywrX_H78-2V-H1el5xOBfSKinDnI8af5iRS2Gc"
try:
    sheet = client.open_by_url(sheet_url).sheet1
except Exception as e:
    st.error("❌ Could not open the Google Sheet.")
    st.code(str(e))
    st.stop()

# ---------- UI Header ----------
st.set_page_config(page_title="Faculty Feedback - AI Workshop", layout="wide")
st.title("📝 Faculty Feedback Form")
st.subheader("Two-Day Workshop: Teaching Transformation – AI Tools for NEP Pedagogy")

st.markdown("""
### Please rate the following statements based on your experience.  
**Likert Scale Meaning:**  
- 1 = Poor  
- 2 = Fair  
- 3 = Satisfactory  
- 4 = Good  
- 5 = Excellent  
""")

questions = [
    "The session objectives were clearly defined.",
    "Content was relevant to NEP 2020 pedagogy.",
    "AI tool demonstrations were effective.",
    "Time was managed efficiently.",
    "Interaction and engagement were encouraged.",
    "The resource person(s) explained clearly.",
    "Hands-on activities were useful.",
    "Materials provided were helpful.",
    "Venue and logistics were satisfactory.",
    "Overall, the session met my expectations."
]

# ---------- Feedback Form ----------
with st.form("feedback_form"):
    st.markdown("#### 👤 Faculty Details")
    name = st.text_input("Name")
    dept = st.text_input("Department")
    mobile = st.text_input("Mobile Number")
    email = st.text_input("Email ID")

    st.markdown("#### 📊 Feedback Questions")
    ratings = {}
    for i, q in enumerate(questions, 1):
        st.markdown(f"**{i}. {q}**")
        ratings[f"Q{i}"] = st.slider("", 1, 5, 3, key=f"slider_{i}")

    submitted = st.form_submit_button("Submit Feedback")

    if submitted:
        if not all([name, dept, mobile, email]):
            st.warning("⚠️ Please fill in all details.")
        else:
            ist = pytz.timezone('Asia/Kolkata')
            timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
            row_data = [timestamp, name, dept, mobile, email] + list(ratings.values())
            try:
                sheet.append_row(row_data)
                st.success("✅ Feedback successfully recorded!")
            except Exception as e:
                st.error("❌ Could not write to the Google Sheet.")
                st.code(str(e))

# ---------- Dashboard ----------
st.markdown("---")
st.header("📊 Feedback Summary Dashboard")

try:
    expected_headers = ["Timestamp", "Name", "Department", "Mobile", "Email"] + [f"Q{i}" for i in range(1, 11)]
    data = sheet.get_all_records(expected_headers=expected_headers)
    df = pd.DataFrame(data)

    if df.empty:
        st.info("No responses submitted yet.")
    else:
        st.markdown("### 🌟 Average Ratings Summary")

        averages = df[[f"Q{i}" for i in range(1, 11)]].mean().round(2)

        # --- Summary Chart (All Questions Avg) ---
        fig1, ax1 = plt.subplots(figsize=(10, 4))
        bars = ax1.bar(range(1, 11), averages, color='lightsteelblue', edgecolor='black', linewidth=2)

        ax1.set_title("Average Rating Per Question", fontsize=16, fontweight='bold')
        ax1.set_xlabel("Question Number", fontsize=12, fontweight='bold')
        ax1.set_ylabel("Average Score", fontsize=12, fontweight='bold')
        ax1.set_xticks(range(1, 11))
        ax1.set_ylim(1, 5)
        ax1.tick_params(axis='both', labelsize=11, width=2)
        for side in ['bottom', 'left']:
            ax1.spines[side].set_linewidth(2)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        for i, bar in enumerate(bars):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                     f"{bar.get_height():.2f}", ha='center', fontsize=10, fontweight='bold')

        st.pyplot(fig1)

        st.markdown("### 🧾 Detailed Average Table")
        avg_df = pd.DataFrame({
            "Question": [questions[i - 1] for i in range(1, 11)],
            "Average Score": averages.values
        })
        st.dataframe(avg_df, use_container_width=True)

        # --- Question-wise Charts ---
        st.markdown("### 🎯 Question-Wise Response Breakdown")

        for i in range(1, 11):
            q_col = f"Q{i}"
            question = questions[i - 1]
            response_counts = df[q_col].value_counts().sort_index()
            all_ratings = [response_counts.get(r, 0) for r in range(1, 6)]

            fig, ax = plt.subplots(figsize=(6, 2.5))
            bars = ax.bar(range(1, 6), all_ratings,
                          color=["#FF4B4B", "#FF914D", "#FFD93D", "#6BCB77", "#4D96FF"],
                          edgecolor='black', linewidth=1.5)

            ax.set_title(f"{i}. {question}", fontsize=12, fontweight="bold")
            ax.set_xlabel("Rating (1=Poor to 5=Excellent)", fontsize=10, fontweight="bold")
            ax.set_ylabel("Responses", fontsize=10, fontweight="bold")
            ax.set_xticks(range(1, 6))
            ax.set_ylim(0, max(all_ratings) + 1)
            ax.tick_params(axis='both', labelsize=10)

            for bar, val in zip(bars, all_ratings):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        str(val), ha='center', fontsize=9, fontweight='bold')

            st.pyplot(fig)

except Exception as e:
    st.error("⚠️ Could not load dashboard or charts.")
    st.code(str(e))
