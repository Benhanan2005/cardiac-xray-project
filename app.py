from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import numpy as np
import cv2
import os
import random
from fpdf import FPDF
import io

app = Flask(__name__)
CORS(app)

# ✅ HOME ROUTE (fixes Not Found)
@app.route("/")
def home():
    return '''
    <h2>Cardiac X-ray Detection</h2>
    <form action="/predict" method="post" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <br><br>
        <button type="submit">Upload & Predict</button>
    </form>
    '''

# ✅ PREDICT ROUTE
@app.route('/predict', methods=['POST'])
def predict():
    file = request.files['file']

    # Save file
    os.makedirs("uploads", exist_ok=True)
    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)

    # Image processing
    img = cv2.imread(filepath)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.reshape(img, (1, 224, 224, 3))

    # ✅ Dummy prediction (no model)
    prediction_value = random.random()

    if prediction_value > 0.5:
        result = "Abnormal 🔴"
        confidence = round(prediction_value * 100, 2)

        doctors = [
            {"name": "Dr. Ravi Kumar", "hospital": "City Hospital", "phone": "9876543210"},
            {"name": "Dr. Anjali Sharma", "hospital": "Heart Care Clinic", "phone": "9123456789"}
        ]
    else:
        result = "Normal 🟢"
        confidence = round((1 - prediction_value) * 100, 2)
        doctors = []

    return f"""
<h2>Result</h2>
<p>Prediction: {result}</p>
<p>Confidence: {confidence}%</p>

<h3>Doctors:</h3>
<ul>
{''.join([f"<li>{d['name']} - {d['hospital']} ({d['phone']})</li>" for d in doctors])}
</ul>

<br>
<a href="/">Go Back</a>
"""

# ✅ DOWNLOAD REPORT
@app.route('/download-report', methods=['POST'])
def download_report():
    data = request.json

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt="X-ray Report", ln=True)
    pdf.cell(200, 10, txt=f"Prediction: {data['prediction']}", ln=True)
    pdf.cell(200, 10, txt=f"Confidence: {data['confidence']}%", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="report.pdf")

# ✅ RUN APP
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)