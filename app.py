import streamlit as st
import numpy as np
import cv2
import os
import random
from fpdf import FPDF
import io
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import re

# 📁 Upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Dummy prediction function (from your original code)
def predict_heart_attack(img_path):
    img = cv2.imread(img_path)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.reshape(img, (1, 224, 224, 3))
    prediction = random.random()
    if prediction > 0.5:
        result = "Abnormal 🔴"
        confidence = round(prediction * 100, 2)
        probability = confidence  # Heart attack prob
        doctors = [
            {"name": "Dr. Ravi Kumar", "hospital": "City Hospital", "phone": "9876543210"},
            {"name": "Dr. Anjali Sharma", "hospital": "Heart Care Clinic", "phone": "9123456789"}
        ]
    else:
        result = "Normal 🟢"
        confidence = round((1 - prediction) * 100, 2)
        probability = 100 - confidence
        doctors = []
    return result, probability, doctors

# PDF generation (updated)
def generate_pdf(prediction, confidence, age, cholesterol, insight):
    prediction_clean = re.sub(r'[^\x00-\x7F]+', '', prediction)  # Strip emojis
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style='B')
    pdf.cell(200, 10, txt="Cardiac X-ray Diagnostic Report", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True, align='R')
    pdf.cell(200, 10, txt=f"Patient Age: {age} | Cholesterol: {cholesterol} mg/dL", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Prediction Results", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Status: {prediction_clean}", ln=True)
    pdf.cell(200, 10, txt=f"Confidence: {confidence}%", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="AI Insights", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=insight)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=14, style='B')
    pdf.cell(200, 10, txt="Recommendations", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt="Consult a cardiologist immediately. Follow a heart-healthy diet, exercise regularly, and monitor blood pressure. Avoid smoking and manage stress.")
    pdf.ln(10)
    
    pdf.set_font("Arial", size=10, style='I')
    pdf.cell(200, 10, txt="Disclaimer: This is an AI-generated report for informational purposes only. Consult a healthcare professional for diagnosis.", ln=True)
    
    pdf_data = pdf.output(dest='S').encode('latin-1')
    return io.BytesIO(pdf_data)

# Streamlit config for dark theme
st.set_page_config(page_title="AI-Based Cardiac Abnormality Detection Using Chest X-Ray Images", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
.main {background-color: #121212; color: #ffffff;}
.sidebar .sidebar-content {background-color: #1e1e1e;}
.stButton>button {background-color: #4facfe; color: white;}
.card {background-color: #2c2c2c; padding: 20px; border-radius: 10px; margin: 10px;}
</style>
""", unsafe_allow_html=True)

# Sidebar: Diagnostic Settings
st.sidebar.title("Diagnostic Settings")
domain = st.sidebar.selectbox("Health Domain", ["Cardiovascular", "Endocrine", "Musculoskeletal", "Gastrointestinal", "Neurological"])
ai_mode = st.sidebar.checkbox("Enable AI Mode", value=True)
st.sidebar.subheader("Inputs")
lab_tests = st.sidebar.checkbox("Lab Tests")
medications = st.sidebar.checkbox("Medications")
allergies = st.sidebar.checkbox("Allergies")
st.sidebar.subheader("Parameters")
parameters = st.sidebar.multiselect("Select Parameters", ["CSF Analysis", "Vitamin Levels", "Neurotransmitters"], default=["CSF Analysis"])

# Main Layout
col1, col2 = st.columns([1, 2])

# Center: Main Prediction Card
with col2:
    st.header("AI-Based Cardiac Abnormality Detection Using Chest X-Ray Images")
    uploaded_file = st.file_uploader("Upload Cardiac X-ray", type=["png", "jpg", "jpeg"])
    if uploaded_file:
        # Save and predict
        filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        result, probability, doctors = predict_heart_attack(filepath)
        
        # Prediction Card
        st.markdown(f"""
        <div class="card">
            <h3>Heart Attack Prediction</h3>
            <h1 style="color: {'#ff4d4d' if probability > 50 else '#4dff4d'};">{probability}% Probability</h1>
            <p>Status: {result}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Charts in Card
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=probability,
            title={'text': "Risk Level"},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "red" if probability > 50 else "green"}}
        ))
        st.plotly_chart(fig)
        
        # Image Display
        st.image(uploaded_file, caption="Uploaded X-ray", width=200)
        
        # Innovative: AI Insights & Recommendations
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("AI Insights & Recommendations")
        
        # User Inputs for Refinement
        st.write("**Refine Your Risk Assessment:**")
        user_age = st.number_input("Enter Age", min_value=0, max_value=120, value=50)
        user_chol = st.number_input("Cholesterol Level (mg/dL)", min_value=100, max_value=400, value=200)
        
        # Dynamic Suggestions with Links
        if probability > 70:
            insight = "High risk! Immediate action needed: Schedule a cardiologist visit, start low-sodium diet, and monitor vitals daily. [Learn more](https://www.heart.org/en/health-topics/heart-attack)."
        elif probability > 50:
            insight = "Moderate risk. Consider genetic counseling, regular exercise (30 min/day), and BP checks. [Resources](https://www.cdc.gov/heartdisease/index.htm)."
        else:
            insight = "Low risk. Maintain with balanced diet, no smoking, and annual check-ups. [Tips](https://www.mayoclinic.org/healthy-lifestyle)."
        st.write(f"**AI Insight:** {insight}")
        
        # Interactive Risk Sliders
        st.write("**Adjust Additional Factors:**")
        age_factor = st.slider("Age Impact", 0, 100, int(user_age * 0.5), key="age_slider")
        lifestyle_factor = st.slider("Lifestyle Impact", 0, 100, 30, key="lifestyle_slider")
        chol_factor = st.slider("Cholesterol Impact", 0, 100, int((user_chol - 150) / 2.5), key="chol_slider")
        adjusted_risk = min(100, probability + age_factor * 0.1 + lifestyle_factor * 0.05 + chol_factor * 0.02)
        st.write(f"Adjusted Risk: {round(adjusted_risk, 2)}%")
        
        # Risk Factor Chart
        factors = {"Age": age_factor, "Lifestyle": lifestyle_factor, "Cholesterol": chol_factor}
        fig_factors = px.bar(x=list(factors.keys()), y=list(factors.values()), title="Risk Factor Contributions")
        st.plotly_chart(fig_factors)
        
        # Generate Personalized Plan
        if st.button("Generate Personalized Plan"):
            plan = f"**Your Plan:**\n- Age {user_age}: {'Focus on cardio exercises.' if user_age > 50 else 'Build healthy habits early.'}\n- Cholesterol {user_chol}: {'Reduce saturated fats.' if user_chol > 240 else 'Maintain levels.'}\n- Overall: Consult doctor for tailored advice."
            st.text_area("Personalized Health Plan", plan, height=100)
        
        # Mini Chatbot
        st.write("**Ask AI Assistant:**")
        user_query = st.text_input("Type your question (e.g., 'What is heart attack?')", key="chat_input")
        if user_query:
            responses = {
                "what is heart attack": "A heart attack occurs when blood flow to the heart is blocked, often by a clot. Symptoms: chest pain, shortness of breath.",
                "symptoms": "Common: chest pain, arm pain, sweating, nausea. Seek help immediately if suspected.",
                "prevention": "Eat healthy (fruits/veggies), exercise regularly, avoid smoking, manage stress and diabetes.",
                "diet tips": "Low in salt/sugar, high in fiber. Examples: Mediterranean diet with fish, nuts, olive oil.",
                "exercise": "Aim for 150 min/week of moderate activity, like walking or cycling.",
                "when to see doctor": "If you have chest pain, high BP, or family history of heart disease."
            }
            response = responses.get(user_query.lower(), "I'm sorry, I don't have info on that. Consult a doctor for personalized advice.")
            st.write(f"AI: {response}")
        
        # Download Report Button
        if st.button("Download Report"):
            pdf_buffer = generate_pdf(result, probability, user_age, user_chol, insight)
            st.download_button("Download PDF", pdf_buffer, "report.pdf")
        st.markdown('</div>', unsafe_allow_html=True)

# Left Column: Connected Modules
with col1:
    st.subheader("Connected Modules")
    
    # Genetics Module
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("**Genetics**")
    genetic_factors = ["Family History", "Gene Variant A", "Gene Variant B"]
    st.bar_chart({factor: random.randint(10, 90) for factor in genetic_factors})
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Lab Tests Module
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("**Lab Tests**")
    if lab_tests:
        lab_data = {"Cholesterol": 200, "Blood Pressure": 140, "Glucose": 100}
        fig_lab = px.bar(x=list(lab_data.keys()), y=list(lab_data.values()), title="Lab Results")
        st.plotly_chart(fig_lab)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Simulation Results Module
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("**Simulation Results**")
    # 3D Heart Model (simulated with Plotly)
    theta = np.linspace(0, 2*np.pi, 100)
    phi = np.linspace(0, np.pi, 50)
    x = np.outer(np.cos(theta), np.sin(phi))
    y = np.outer(np.sin(theta), np.sin(phi))
    z = np.outer(np.ones(np.size(theta)), np.cos(phi))
    fig_3d = go.Figure(data=[go.Surface(x=x, y=y, z=z, colorscale='Reds', opacity=0.7)])
    fig_3d.update_layout(title="3D Heart Model", scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    st.plotly_chart(fig_3d)
    
    # Cardiogram
    time = np.linspace(0, 10, 100)
    signal = np.sin(time) + 0.5 * np.random.randn(100)
    fig_sim = px.line(x=time, y=signal, title="Cardiogram Simulation")
    st.plotly_chart(fig_sim)
    
    # Risk Factors
    st.write("**Risk Drivers**")
    primary_risks = ["High BP", "Smoking"]
    medium_risks = ["Age", "Cholesterol"]
    st.write("Primary:", ", ".join(primary_risks))
    st.write("Medium:", ", ".join(medium_risks))
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Doctors (if available)
    if 'doctors' in locals() and doctors:
        st.subheader("Recommended Doctors")
        for doc in doctors:
            st.write(f"{doc['name']} - {doc['hospital']} ({doc['phone']})")

# Bottom: Timeline Forecast (only show after upload)
if uploaded_file:
    st.header("Forecast Timeline")
    dates = [datetime.now() + timedelta(days=i) for i in range(30)]
    forecast_probs = [probability + random.randint(-10, 10) for _ in range(30)]
    fig_timeline = px.line(x=dates, y=forecast_probs, title="Heart Attack Risk Over Time")
    st.plotly_chart(fig_timeline)