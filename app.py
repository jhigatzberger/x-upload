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

@app.route('/create', methods=['POST'])
def create_post():
    if 'file' not in request.files or 'text' not in request.form:
        return jsonify({"error": "Missing file or text"}), 400
    
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
    app.run(debug=True)
