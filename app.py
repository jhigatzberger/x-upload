import os
from flask import Flask, request, jsonify
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Authenticate with Twitter API
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
    if request_api_key != API_KEY:
        return False
    return True

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/create', methods=['POST'])
def create_post():
    # API key validation
    if not check_api_key():
        return jsonify({"error": "Unauthorized: Invalid API Key"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "Missing file"}), 400
    
    if 'text' not in request.form:
        return jsonify({"error": "Missing text"}), 400

    file = request.files['file']
    text = request.form['text']

    # Save file temporarily
    file_path = "temp_image.jpg"
    file.save(file_path)

    try:
        # Upload media
        media = api.media_upload(filename=file_path)
        
        # Create tweet with media
        tweet = api.update_status(status=text, media_ids=[media.media_id])
        
        # Cleanup
        os.remove(file_path)

        return jsonify({"message": "Tweet posted successfully", "tweet_id": tweet.id_str})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
