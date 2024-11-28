import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from tensorflow.keras.models import load_model
import numpy as np
import cv2
import tempfile
import logging

# Initialize Flask app and specify the template folder
app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'frontend'))
CORS(app)  # Enable CORS for all routes

# Set up logging
logging.basicConfig(level=logging.INFO)

# Load the saved model
MODEL_PATH = "deepfake_detector_balanced.keras"
try:
    model = load_model(MODEL_PATH)
    logging.info("Model loaded successfully!")
except Exception as e:
    logging.error(f"Failed to load model: {e}")
    raise

# Ensure a temporary directory exists
TEMP_DIR = tempfile.gettempdir()  # Use cross-platform temporary directory

@app.route("/")
def home():
    return render_template("deepfake.html")


# Preprocess image
def preprocess_image(image_path, image_size=(128, 128)):
    try:
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Failed to read image from {image_path}")
        image = cv2.resize(image, image_size) / 255.0
        image = image.reshape(1, *image_size, 3)
        return image
    except Exception as e:
        logging.error(f"Error in image preprocessing: {e}")
        raise


# Preprocess video frames
def preprocess_frames(frames, image_size=(128, 128)):
    processed_frames = []
    for frame in frames:
        frame = cv2.resize(frame, image_size) / 255.0
        processed_frames.append(frame.reshape(1, *image_size, 3))
    return processed_frames


# Extract frames from video
def extract_frames(video_path, frame_rate=30):
    frames = []
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Unable to open video file: {video_path}")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        if frame_count % frame_rate == 0:  # Extract every `frame_rate` frame
            frames.append(frame)

        frame_count += 1

    cap.release()
    return frames


# Predict video classification
def classify_video(video_path):
    frames = extract_frames(video_path, frame_rate=30)  # Extract 1 frame per second
    if not frames:
        raise ValueError("No frames extracted from video")

    processed_frames = preprocess_frames(frames)
    fake_count = 0
    real_count = 0

    for frame in processed_frames:
        prediction = model.predict(frame)[0]
        if prediction[1] > 0.5:  # FAKE confidence
            fake_count += 1
        else:  # REAL confidence
            real_count += 1

    total_frames = fake_count + real_count
    result = "FAKE" if fake_count > real_count else "REAL"
    confidence = max(fake_count, real_count) / total_frames * 100

    return {"result": result, "confidence": f"{confidence:.2f}%"}


# Endpoint to handle image prediction
@app.route("/predict-image", methods=["POST"])
def predict_image():
    if "file" not in request.files:
        logging.error("No file uploaded.")
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_path = os.path.join(TEMP_DIR, file.filename)
    file.save(file_path)

    try:
        logging.info(f"Processing image: {file.filename}")
        image = preprocess_image(file_path)
        prediction = model.predict(image)[0]
        fake_confidence = prediction[1]
        real_confidence = prediction[0]
        result = "FAKE" if fake_confidence > 0.5 else "REAL"

        response = {
            "result": result,
            "confidence": {
                "FAKE": f"{fake_confidence * 100:.2f}%",
                "REAL": f"{real_confidence * 100:.2f}%"
            }
        }
        logging.info(f"Image prediction result: {response}")
    except Exception as e:
        logging.error(f"Error during image prediction: {e}")
        return jsonify({"error": "Failed to process image"}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify(response)


# Endpoint to handle video prediction
@app.route("/predict-video", methods=["POST"])
def predict_video():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    file_path = os.path.join(TEMP_DIR, file.filename)
    file.save(file_path)

    try:
        response = classify_video(file_path)
        logging.info(f"Video prediction result: {response}")
    except Exception as e:
        logging.error(f"Error during video prediction: {e}")
        return jsonify({"error": "Failed to process video"}), 500
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

    return jsonify(response)


# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "running", "model_loaded": os.path.exists(MODEL_PATH)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
