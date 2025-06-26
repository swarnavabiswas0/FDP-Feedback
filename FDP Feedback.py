import streamlit as st
import pandas as pd
import gspread
import pytz
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# ---------- Google Sheets Auth ----------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("pdf-auto-uploader-0835284833d4.json", scope)
client = gspread.authorize(creds)

# ---------- Sheet Setup ----------
sheet_name = "Faculty Feedback Responses"
try:
    sheet = client.open(sheet_name).sheet1
except gspread.exceptions.SpreadsheetNotFound:
    sheet = client.create(sheet_name).sheet1
    sheet.append_row(["Timestamp", "Name", "Department", "Mobile", "Email"] + [f"Q{i}" for i in range(1, 11)])

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
        st.markdown(f"**{i}. {q}**  \n*(1 = Poor, 5 = Excellent)*")
        ratings[f"Q{i}"] = st.slider("", 1, 5, 3, key=f"slider_{i}")

    submitted = st.form_submit_button("Submit Feedback")

    if submitted:
        if not all([name, dept, mobile, email]):
            st.warning("⚠️ Please fill in all details before submitting.")
        else:
            ist = pytz.timezone('Asia/Kolkata')
            timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

            row_data = [timestamp, name, dept, mobile, email] + list(ratings.values())
            sheet.append_row(row_data)
            st.success("✅ Feedback successfully recorded in Google Sheet!")
