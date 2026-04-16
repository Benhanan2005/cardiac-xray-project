from flask import Flask, request, send_from_directory, send_file
from flask_cors import CORS
import numpy as np
import cv2
import os
import random
from fpdf import FPDF
import io

app = Flask(__name__)
CORS(app)

# 📁 Upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# ✅ Home Page
@app.route("/")
def home():
    return '''
    <html>
    <head>
        <title>Cardiac X-ray Detection</title>
        <style>
            body {
                font-family: Arial;
                background: linear-gradient(to right, #4facfe, #00f2fe);
                text-align: center;
                padding-top: 100px;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                width: 400px;
                margin: auto;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
            }
            button {
                background: #4facfe;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    </head>

    <body>
        <div class="container">
            <h2>Cardiac X-ray Detection</h2>
            <form action="/predict" method="post" enctype="multipart/form-data">
                <input type="file" name="file" required>
                <br><br>
                <button type="submit">Upload & Predict</button>
            </form>
        </div>
    </body>
    </html>
    '''

# ✅ Predict Route
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'GET':
        return "Please upload image from home page"

    file = request.files['file']

    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Image processing
    img = cv2.imread(filepath)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.reshape(img, (1, 224, 224, 3))

    # Dummy prediction
    prediction = random.random()

    if prediction > 0.5:
        result = "Abnormal 🔴"
        confidence = round(prediction * 100, 2)
        doctors = [
            {"name": "Dr. Ravi Kumar", "hospital": "City Hospital", "phone": "9876543210"},
            {"name": "Dr. Anjali Sharma", "hospital": "Heart Care Clinic", "phone": "9123456789"}
        ]
    else:
        result = "Normal 🟢"
        confidence = round((1 - prediction) * 100, 2)
        doctors = []

    # Doctor HTML
    doctor_html = "".join(
        [f"<li>{d['name']} - {d['hospital']} ({d['phone']})</li>" for d in doctors]
    )

    # Result Page
    return f"""
    <html>
    <head>
    <style>
    body {{
        font-family: Arial;
        background: linear-gradient(to right, #43e97b, #38f9d7);
        text-align: center;
        padding-top: 50px;
    }}
    .box {{
        background: white;
        padding: 30px;
        border-radius: 10px;
        width: 400px;
        margin: auto;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.2);
    }}
    button {{
        background: #43e97b;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        cursor: pointer;
    }}
    </style>
    </head>

    <body>
    <div class="box">
        <h2>Result</h2>

        <h3>Uploaded Image:</h3>
        <img src="/uploads/{file.filename}" width="200">

        <p><b>Prediction:</b> {result}</p>
        <p><b>Confidence:</b> {confidence}%</p>

        <h3>Doctors:</h3>
        <ul>{doctor_html}</ul>

        <br>

        <form action="/download-report" method="post">
            <input type="hidden" name="prediction" value="{result}">
            <input type="hidden" name="confidence" value="{confidence}">
            <button type="submit">Download Report 📄</button>
        </form>

        <br><br>
        <a href="/">Go Back</a>
    </div>
    </body>
    </html>
    """

# ✅ PDF Download
@app.route('/download-report', methods=['POST'])
def download_report():
    prediction = request.form['prediction']
    confidence = request.form['confidence']

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)

    pdf.cell(200, 10, txt="Cardiac X-ray Report", ln=True)
    pdf.cell(200, 10, txt=f"Prediction: {prediction}", ln=True)
    pdf.cell(200, 10, txt=f"Confidence: {confidence}%", ln=True)

    buffer = io.BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="report.pdf")

# ✅ Run
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)