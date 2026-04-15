import tensorflow as tf
import numpy as np
import cv2

model = tf.keras.models.load_model('model/xray_model.h5')

img_path = 'test.jpg'

img = cv2.imread(img_path)
img = cv2.resize(img, (224,224))
img = img / 255.0
img = np.reshape(img, (1,224,224,3))

prediction = model.predict(img)[0][0]

print("Prediction Value:", prediction)

# Risk logic
if prediction < 0.3:
    print("✅ NORMAL - Low Risk 🟢")

elif prediction < 0.7:
    print("⚠️ Abnormal - Medium Risk 🟡")

else:
    print("🚨 Abnormal - High Risk 🔴")