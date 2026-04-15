from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import cv2
import os

app = Flask(__name__)
CORS(app)

# Load model
model = tf.keras.models.load_model('model/xray_model.h5')

@app.route('/predict', methods=['POST'])
def predict():
    print("HELLO") 
    file = request.files['file']

    filepath = os.path.join("uploads", file.filename)
    os.makedirs("uploads", exist_ok=True)
    file.save(filepath)

    # Image processing
    img = cv2.imread(filepath)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.reshape(img, (1, 224, 224, 3))

    # Prediction
    prediction = model.predict(img)[0][0]

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

    return jsonify({
        "prediction": result,
        "confidence": confidence,
        "doctors": doctors
    })


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0", port=5050)

    from flask import send_file
from fpdf import FPDF
import io

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
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)   # ✅ THIS IS IMPORTANT