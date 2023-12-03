from app.models.user import User  # Import your User model
from flask import jsonify, request
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User
import jwt
import os
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file
load_dotenv()
# Get the JWT secret key from environment variables
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
# Set token expiration time (in seconds), for example, 1 day
TOKEN_EXPIRATION = 86400  # 24 hours * 60 minutes * 60 seconds

user_routes = Blueprint('user_routes', __name__)


@user_routes.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        if data:
            name = data.get('name')
            email = data.get('email')
            password = data.get('password')

            if not (name and email and password):
                return jsonify({'message': 'Name, email, and password are required'}), 400

            existing_user = User.find_by_email(email)
            if existing_user:
                return jsonify({'message': 'User already exists'}), 400

            # Determine the role based on the email domain
            if email.endswith('@intellihirehub.com'):
                role = 'hiring manager'
            elif email.endswith('@gmail.com'):
                role = 'job seeker'
            else:
                return jsonify({'message': 'Invalid email domain'}), 400

            # Hash the password before saving it to the database
            hashed_password = generate_password_hash(password)

            new_user = User(name, email, hashed_password,
                            role)  # Save the hashed password
            new_user.save()

            # Additional data to send along with the success message
            user_details = {
                'name': name,
                'email': email,
                'role': role
            }

            return jsonify({'message': 'User registered successfully', 'user': user_details})
        else:
            return jsonify({'message': 'Invalid data received'}), 400


@user_routes.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        if data:
            email = data.get('email')
            password = data.get('password')

            if not (email and password):
                return jsonify({'message': 'Email and password are required'}), 400

            user = User.find_by_email(email)
            if user and check_password_hash(user['password'], password):
                user_id = str(user['_id'])
                role = str(user['role'])

                # Set token expiration time
                expiration = datetime.datetime.utcnow(
                ) + datetime.timedelta(days=1)  # 1 day expiration

                # Generate token with expiration time
                payload = {
                    'user_id': user_id,
                    'exp': expiration
                }
                token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')

                return jsonify({'message': 'Login successful', 'token': token, 'role': role})
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
        else:
            return jsonify({'message': 'Invalid data received'}), 400


@user_routes.route('/user-details', methods=['GET'])
def user_details():
    token = request.headers.get('Authorization')
    # print(token)
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']

        # Fetch user details based on user_id
        user = User.find_by_id(user_id)
        # print(user)
        if user:
            user_details = {
                'id': str(user['_id']),  # Assuming '_id' is MongoDB's ObjectId
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
            return jsonify({'message': 'User details fetched', 'user_details': user_details})
        else:
            return jsonify({'message': 'User not found'}), 404

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401


@user_routes.route('/user-details', methods=['PATCH'])
def update_user_details():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']

        user = User.find_by_id(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'message': 'Invalid data received'}), 400

        # Check if any specific field needs to be updated
        if 'name' in data:
            user['name'] = data['name']
        if 'email' in data:
            user['email'] = data['email']

        # Save the updated user data
        User.update(user_id, {'name': user['name'], 'email': user['email']})

        user_details = {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'role': user['role']
        }
        return jsonify({'message': 'User details updated', 'user_details': user_details})

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
