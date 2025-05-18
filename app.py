from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Load environment variables
load_dotenv()

# Initialize MongoDB client
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017'))  # Fallback to local MongoDB
db = client['portfolio_db']
messages_collection = db['messages']

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/style.css')
def serve_css():
    return app.send_static_file('style.css')

@app.route('/script.js')
def serve_js():
    return app.send_static_file('script.js')

@app.route('/api/messages', methods=['GET'])
def get_messages():
    try:
        messages = messages_collection.find().sort('timestamp', -1)
        messages_list = [
            {
                'id': str(msg['_id']),
                'name': msg['name'],
                'email': msg['email'],
                'message': msg['message'],
                'timestamp': msg['timestamp']
            }
            for msg in messages
        ]
        return jsonify({'success': True, 'messages': messages_list}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
