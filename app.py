import os
from flask import Flask, request, jsonify
import tweepy
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import base64

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

bearer_token = os.getenv("BEARER_TOKEN")

# Twitter API authentication
auth = tweepy.OAuth1UserHandler(
    os.getenv("CONSUMER_KEY"),
    os.getenv("CONSUMER_SECRET"),
    os.getenv("ACCESS_TOKEN"),
    os.getenv("ACCESS_TOKEN_SECRET")
)
api = tweepy.API(auth)
API_KEY = os.getenv("API_KEY")  # Load API Key from .env

def check_api_key():
    """Validate API key in the request headers."""
    request_api_key = request.headers.get("X-API-KEY")
    return request_api_key == API_KEY

def allowed_file(filename):
    """Check if file extension is allowed."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create', methods=['POST'])
def create_post():
    if not check_api_key():
        return jsonify({"error": "Unauthorized: Invalid API Key"}), 401

    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    # Extract values from JSON
    text = data.get("text")
    base64_string = data.get("file")  # Base64-encoded image string

    if not text:
        return jsonify({"error": "Missing text"}), 400

    if not base64_string:
        return jsonify({"error": "Missing file"}), 400

    # Validate and decode Base64 string
    if not is_valid_base64(base64_string):
        return jsonify({"error": "Invalid Base64 string"}), 400

    try:
        binary_data = base64.b64decode(base64_string)

        # Save binary data as an image file
        filename = "uploaded_image.jpg"
        file_path = os.path.join(UPLOAD_FOLDER, filename)

        with open(file_path, "wb") as f:
            f.write(binary_data)

        print("Base64 file successfully decoded and saved")

    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Upload to Twitter
    try:
        media = api.media_upload(filename=file_path)
        os.remove(file_path)  # Cleanup
        return jsonify({"message": "Media uploaded successfully", "media_id": media.media_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def is_valid_base64(base64_string):
    """Check if a given string is valid Base64."""
    try:
        base64.b64decode(base64_string, validate=True)
        return True
    except Exception:
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
