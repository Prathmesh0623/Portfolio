from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
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

# Email configuration
app.config['SMTP_SERVER'] = 'smtp.gmail.com'
app.config['SMTP_PORT'] = 587
app.config['SMTP_EMAIL'] = os.getenv('SMTP_EMAIL', 'prathmeshkl2003@gmail.com')  # Your email for SMTP authentication
app.config['RECEIVER_EMAIL'] = os.getenv('RECEIVER_EMAIL', 'prathmeshkl2003@gmail.com')  # Your email to receive messages
app.config['EMAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/style.css')
def serve_css():
    return app.send_static_file('style.css')

@app.route('/script.js')
def serve_js():
    return app.send_static_file('script.js')

@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not name or not email or not message:
            return jsonify({'success': False, 'error': 'All fields are required'}), 400

        # Store in MongoDB
        message_doc = {
            'name': name,
            'email': email,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        messages_collection.insert_one(message_doc)

        # Send email notification
        email_body = (
            f"New Contact Form Submission\n\n"
            f"From: {name}\n"
            f"Email: {email}\n"
            f"Message:\n{message}\n\n"
            f"Received: {message_doc['timestamp']}"
        )
        msg = MIMEText(email_body)
        msg['Subject'] = 'New Contact Form Submission'
        msg['From'] = f"{name} <{email}>"  # Display user's name and email
        msg['To'] = app.config['RECEIVER_EMAIL']
        msg['Reply-To'] = email  # User's email for replies

        # Use STARTTLS with port 587
        with smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT']) as server:
            server.starttls()
            server.login(app.config['SMTP_EMAIL'], app.config['EMAIL_PASSWORD'])
            server.sendmail(app.config['SMTP_EMAIL'], app.config['RECEIVER_EMAIL'], msg.as_string())

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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