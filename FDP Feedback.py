import streamlit as st
import pandas as pd
import gspread
from datetime import datetime
import pytz
from oauth2client.service_account import ServiceAccountCredentials
import json

# ---------- Load service account from uploaded file ----------
with open("streamlit-feedback-bot-f6777d687e79.json") as source:
    json_key = json.load(source)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json_key, scope)
client = gspread.authorize(creds)

# ---------- Open your shared Google Sheet ----------
sheet_url = "https://docs.google.com/spreadsheets/d/1FyNxVywrX_H78-2V-H1el5xOBfSKinDnI8af5iRS2Gc"

try:
    sheet = client.open_by_url(sheet_url).sheet1
except Exception as e:
    st.error("❌ Could not open the Google Sheet.")
    st.code(str(e))
    st.stop()

# ---------- Streamlit App UI ----------
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
            # Timestamp in IST
            ist = pytz.timezone('Asia/Kolkata')
            timestamp = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")

            row_data = [timestamp, name, dept, mobile, email] + list(ratings.values())
            try:
                sheet.append_row(row_data)
                st.success("✅ Feedback successfully recorded in Google Sheet!")
            except Exception as e:
                st.error("❌ Could not write to the Google Sheet.")
                st.code(str(e))
