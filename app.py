import random
import uuid
import hashlib

from flask import Flask, jsonify, request

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_redis import FlaskRedis

from google import google
from models.user import User

app = Flask(__name__)
app.config.from_object('config')

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
redis_store = FlaskRedis(app)

SUBJECTS = ["fruits", "basketball", "cyber"]

SUBJECT_TO_LINK = {}


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    body = request.get_json(silent=True)
    username = body['username']
    password = body['password']
    user_subject = body['subject']
    images = []
    for subject in SUBJECTS:
        subject_images = random.sample(google.search_images(subject), 3)
        for s_image in subject_images:
            SUBJECT_TO_LINK[subject] = s_image.link
            images.append(s_image.link)
    return jsonify({'username': username,
                    'images': images
                    })


@app.route('/login', methods=['POST'])
def login():
    body = request.get_json(silent=True)
    username = body['username']
    password = body['password']
    images = []
    session_token = uuid.uuid4()
    user = User.query.filter_by(username=username).first_or_404()
    if user.check_password_hash(password.encode('utf-8')):
        for subject in SUBJECTS:
            subject_image_link = random.choice(google.search_images(subject)).link
            session_token_subject_key = hashlib.sha256(bytes(session_token + subject_image_link)).hexdigest()
            redis_store[session_token_subject_key] = subject
            images.append(subject_image_link)
        return jsonify({
            'username': username,
            'images': images,
            'session_token': session_token
        })


@app.route('/image_2fa', methods=['POST'])
def image_2fa():
    body = request.get_json(silent=True)
    username = body['username']
    session_token = body['session_token']
    chosen_image = body['chosen_image']
    session_token_subject_key = hashlib.sha256(bytes(session_token + chosen_image)).hexdigest()
    session_image_subject = redis_store[session_token_subject_key]
    user = User.query.filter_by(username=username).first_or_404()
    if user.check_subject_hash(session_image_subject.encode('utf-8')):
        return jsonify({
            'success': True
        })
    return jsonify({
        'success': False
    })


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
