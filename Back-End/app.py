from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from tensorflow.keras.models import load_model
import cv2
import numpy as np
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the saved model
model = load_model("deepfake_detector_balanced.keras")  # Ensure the .keras file is in the same directory
print("Model loaded successfully!")

# Ensure a temporary directory exists
TEMP_DIR = "C:/temp"
os.makedirs(TEMP_DIR, exist_ok=True)

# Preprocess image
def preprocess_image(image_path, image_size=(128, 128)):
    image = cv2.imread(image_path)
    image = cv2.resize(image, image_size) / 255.0
    image = image.reshape(1, *image_size, 3)
    return image

# Endpoint to handle image prediction
@app.route("/predict-image", methods=["POST"])
def predict_image():
    file = request.files["file"]
    file_path = os.path.join(TEMP_DIR, file.filename)
    file.save(file_path)

    try:
        # Preprocess and predict
        image = preprocess_image(file_path)
        prediction = model.predict(image)[0]  # Get the prediction probabilities
        fake_confidence = prediction[1]  # Confidence for "FAKE" (index 1)
        real_confidence = prediction[0]  # Confidence for "REAL" (index 0)

        # Determine the result
        if fake_confidence > 0.5:
            result = "FAKE"
        else:
            result = "REAL"

        response = {
            "result": result,
            "confidence": {
                "FAKE": f"{fake_confidence * 100:.2f}%",
                "REAL": f"{real_confidence * 100:.2f}%"
            }
        }
        print(response)

    finally:
        os.remove(file_path)  # Clean up

    return jsonify(response)


# Endpoint to handle video prediction
@app.route("/predict-video", methods=["POST"])
def predict_video():
    file = request.files["file"]
    file_path = os.path.join(TEMP_DIR, file.filename)
    file.save(file_path)

    try:
        # Dummy response for testing (replace with actual video classification logic)
        result = "REAL"  # Replace with classify_video logic if implemented
        print({"result": result})

    finally:
        os.remove(file_path)  # Clean up the saved file

    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)