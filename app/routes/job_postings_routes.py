from flask import Blueprint, request, jsonify
from app.models.job_postings import JobPosting
from app.models.user import User
from datetime import datetime
import jwt
import os
from dotenv import load_dotenv
import datetime

# Load environment variables from .env file
load_dotenv()
# Get the JWT secret key from environment variables
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
job_postings_routes = Blueprint('job_postings_routes', __name__)


@job_postings_routes.route('/create-job-posting', methods=['POST'])
def create_job_posting():
    data = request.get_json()

    # Extract data from the request
    job_title = data.get('job_title')
    status = data.get('status')
    start_date_str = data.get('start_date')

    if not all([job_title, status, start_date_str]):
        return jsonify({'message': 'Missing required fields'}), 400

    # Parse and validate the date format
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Get the hiring manager ID from the token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        # Extract the user ID from the token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')

        # Fetch the user details to get the hiring manager ID
        hiring_manager = User.find_by_id(user_id)

        if hiring_manager and hiring_manager['role'] == 'hiring manager':
            hiring_manager_id = str(hiring_manager['_id'])
        else:
            return jsonify({'message': 'User is not a hiring manager'}), 403

        # Create a new job posting with the extracted hiring manager ID
        new_job = JobPosting(
            job_title=job_title,
            status=status,
            start_date=start_date,
            hiring_manager_id=hiring_manager_id
        )

        # Save the job posting
        new_job.save()
        return jsonify({'message': 'Job posting created successfully'}), 201

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'message': 'Failed to create job posting', 'error': str(e)}), 500
