import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import pytz
from oauth2client.service_account import ServiceAccountCredentials
import matplotlib.pyplot as plt

# ---------- Auth from Streamlit secrets ----------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_key = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
client = gspread.authorize(creds)

# ---------- Open Google Sheet ----------
sheet_url = "https://docs.google.com/spreadsheets/d/1FyNxVywrX_H78-2V-H1el5xOBfSKinDnI8af5iRS2Gc"
try:
    sheet = client.open_by_url(sheet_url).sheet1
except Exception as e:
    st.error("❌ Could not open the Google Sheet.")
    st.code(str(e))
    st.stop()

# ---------- Streamlit UI ----------
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
                st.error("❌ Error writing to sheet.")
                st.code(str(e))

# ---------- Feedback Dashboard ----------
st.markdown("---")
st.header("📊 Feedback Summary Dashboard")

try:
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if df.empty:
        st.info("No responses submitted yet.")
    else:
        st.markdown("### Average Ratings per Question")
        averages = df[[f"Q{i}" for i in range(1, 11)]].mean().round(2)

        fig, ax = plt.subplots(figsize=(10, 4))
        bars = ax.bar(range(1, 11), averages, color='skyblue', edgecolor='black')
        ax.set_title("Average Rating Per Question", fontsize=14)
        ax.set_xlabel("Question Number")
        ax.set_ylabel("Average Score")
        ax.set_xticks(range(1, 11))
        ax.set_ylim(1, 5)

        for i, bar in enumerate(bars):
            ax.text(bar.get_x() + 0.25, bar.get_height() + 0.1, f"{averages[i+1]:.2f}", fontsize=9)

        st.pyplot(fig)

        st.markdown("### Detailed Average Ratings Table")
        question_map = {f"Q{i}": questions[i - 1] for i in range(1, 11)}
        avg_df = pd.DataFrame({
            "Question": [question_map[q] for q in averages.index],
            "Average Score": averages.values
        })
        st.dataframe(avg_df, use_container_width=True)

except Exception as e:
    st.error("⚠️ Could not load dashboard.")
    st.code(str(e))
