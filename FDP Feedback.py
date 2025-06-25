import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# ----- Config -----
st.set_page_config(page_title="Faculty Feedback - AI Workshop", layout="wide")

excel_file = "feedback_data.xlsx"
image_dir = "charts"

# ----- Setup Excel and Image Folder -----
if not os.path.exists(excel_file):
    columns = ["Timestamp", "Name", "Department", "Mobile", "Email"] + [f"Q{i}" for i in range(1, 11)]
    pd.DataFrame(columns=columns).to_excel(excel_file, index=False)

if not os.path.exists(image_dir):
    os.makedirs(image_dir)

# ----- Feedback Questions -----
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

# ----- Header -----
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

# ----- Form -----
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
        new_data = pd.DataFrame([[
            datetime.now(), name, dept, mobile, email
        ] + list(ratings.values())],
        columns=["Timestamp", "Name", "Department", "Mobile", "Email"] + list(ratings.keys()))

        existing = pd.read_excel(excel_file)
        updated = pd.concat([existing, new_data], ignore_index=True)
        updated.to_excel(excel_file, index=False)

        st.success("✅ Thank you! Your feedback has been recorded.")

# ----- Dashboard -----
st.markdown("---")
st.header("📊 Feedback Summary Dashboard")

df = pd.read_excel(excel_file)

col1, col2 = st.columns([2, 1])

with col1:
    image_files = []
    for i in range(1, 11):
        fig, ax = plt.subplots(figsize=(5, 2.5))
        ax.hist(df[f"Q{i}"], bins=range(1, 7), edgecolor="black", align='left', rwidth=0.8)
        ax.set_title(f"{i}. {questions[i-1]}", fontweight="bold")
        ax.set_xticks([1, 2, 3, 4, 5])
        ax.set_ylim(0, df.shape[0] + 1)
        ax.set_xlabel("Rating")
        ax.set_ylabel("No. of Responses")
        ax.grid(True, linestyle='--', alpha=0.5)
        for spine in ax.spines.values():
            spine.set_linewidth(2)

        image_path = os.path.join(image_dir, f"Q{i}_feedback.png")
        fig.savefig(image_path, bbox_inches="tight")
        image_files.append(image_path)

        st.pyplot(fig)

with col2:
    st.subheader("🔒 Admin Access for Downloads")
    password_input = st.text_input("Enter admin password:", type="password")

    if password_input == "iqac@bwu":
        st.success("Access granted ✅")

        with open(excel_file, "rb") as f:
            st.download_button("⬇ Download Feedback Excel", f, file_name="faculty_feedback.xlsx")

        import zipfile
        from io import BytesIO
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for img_path in image_files:
                zipf.write(img_path, os.path.basename(img_path))
        zip_buffer.seek(0)

        st.download_button("🖼️ Download All Feedback Charts", data=zip_buffer,
                           file_name="feedback_charts.zip", mime="application/zip")

    elif password_input:
        st.error("❌ Incorrect password")
