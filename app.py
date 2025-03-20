import os
from flask import Flask, request, jsonify
import tweepy
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

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

    # Ensure the request is multipart/form-data
    if not request.content_type.startswith("multipart/form-data"):
        return jsonify({"error": "Invalid content type, must be multipart/form-data"}), 400

    # Debugging: Print received request data
    print("Received headers:", request.headers)
    print("Received form data:", request.form)
    print("Received files:", request.files)

    # Check if file and text are present
    if "file" not in request.files or "text" not in request.form:
        return jsonify({"error": "Missing file or text"}), 400

    file = request.files["file"]
    text = request.form["text"]

    # Ensure a file was uploaded
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    # Secure filename and save to uploads directory
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    try:
        # Upload media to Twitter
        media = api.media_upload(filename=file_path)

        # Create tweet with media
        tweet = api.update_status(status=text, media_ids=[media.media_id])

        # Remove uploaded file after posting
        os.remove(file_path)

        return jsonify({"message": "Tweet posted successfully", "tweet_id": tweet.id_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True)
