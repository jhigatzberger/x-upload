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

    print("Headers:", request.headers)
    print("Content-Type:", request.content_type)
    print("Form Data:", request.form)
    print("Files Data:", request.files)

    if "text" not in request.form:
        return jsonify({"error": "Missing text"}), 400

    text = request.form["text"]
    file_path = None

    # **Case 1: File was correctly uploaded using multipart/form-data**
    if "file" in request.files:
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

    # **Case 2: File is coming as a binary string in the form field**
    elif "file" in request.form:
        try:
            binary_data = request.form["file"].encode("latin1")  # Convert string to bytes
            filename = "uploaded_image.jpg"
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            with open(file_path, "wb") as f:
                f.write(binary_data)  # Save as binary file
            
            print("Binary file successfully extracted and saved")

        except Exception as e:
            return jsonify({"error": "Invalid file format"}), 400

    else:
        return jsonify({"error": "Missing file"}), 400

    # Upload to Twitter
    try:
        media = api.media_upload(filename=file_path)
        tweet = api.update_status(status=text, media_ids=[media.media_id])
        os.remove(file_path)  # Cleanup
        return jsonify({"message": "Tweet posted successfully", "tweet_id": tweet.id_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
