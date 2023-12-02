from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.user import User

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
                # Remove password from the user data before sending it back
                user.pop('password', None)
                return jsonify({'message': 'Login successful', 'user': user})
            else:
                return jsonify({'message': 'Invalid credentials'}), 401
        else:
            return jsonify({'message': 'Invalid data received'}), 400
