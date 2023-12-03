from flask import Blueprint, request, jsonify
from app.models.job_postings import JobPosting
from app.models.user import User
import jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
# Get the JWT secret key from environment variables
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
job_postings_routes = Blueprint('job_postings_routes', __name__)


@job_postings_routes.route('/create-job-posting', methods=['POST'])
def create_job_posting():
    data = request.get_json()

    # Assuming the token is present in the headers with key 'Authorization'
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')

        # Fetch the user details to verify the role and get the hiring manager ID
        user = User.find_by_id(user_id)
        if user and user['role'] == 'hiring manager':
            hiring_manager_id = str(user['_id'])
        else:
            return jsonify({'message': 'User is not a hiring manager'}), 403

        job_title = data.get('job_title')
        status = data.get('status')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        print(start_date, end_date)

        # Check if all required fields are present
        if not all([job_title, status, start_date, end_date]):
            return jsonify({'message': 'Missing required fields'}), 400

        # Create a new JobPosting instance with the extracted data
        new_job = JobPosting(
            job_title=job_title,
            status=status,
            start_date=start_date,
            end_date=end_date,
            hiring_manager_id=hiring_manager_id
        )

        # Save the job posting
        new_job.save()

        return jsonify({'message': 'Job posting created successfully'}), 201

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
    except ValueError:
        return jsonify({'message': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        return jsonify({'message': 'Failed to create job posting', 'error': str(e)}), 500


@job_postings_routes.route('/my-job-postings', methods=['GET'])
def get_my_job_postings():
    # Get the token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        # Decode the token to get the user ID
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')

        # Fetch the user's job postings based on the user ID
        user_job_postings = JobPosting.find_by_hiring_manager(user_id)

        # Format and return the job postings data including jobposting_id
        job_postings_data = []
        for posting in user_job_postings:
            job_postings_data.append({
                '_id': str(posting['_id']),  # Add jobposting_id here
                'job_title': posting['job_title'],
                'status': posting['status'],
                'start_date': str(posting['start_date']),
                'end_date': str(posting['end_date'])
            })

        return jsonify({'job_postings': job_postings_data}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'message': 'Failed to fetch job postings', 'error': str(e)}), 500


@job_postings_routes.route('/update-job-posting/<job_id>', methods=['PUT'])
def update_job_posting(job_id):
    data = request.get_json()

    # Assuming the token is present in the headers with key 'Authorization'
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')

        # Fetch the user details to verify the role
        user = User.find_by_id(user_id)
        if user and user['role'] != 'hiring manager':
            return jsonify({'message': 'User is not authorized to update job postings'}), 403

        # Fetch the job posting by ID
        job = JobPosting.find_by_id(job_id)
        if not job:
            return jsonify({'message': 'Job posting not found'}), 404

        # Update the job posting data
        job_title = data.get('job_title')
        status = data.get('status')
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Update the job posting attributes if provided in the request
        if job_title:
            job['job_title'] = job_title
        if status:
            job['status'] = status
        if start_date:
            job['start_date'] = start_date
        if end_date:
            job['end_date'] = end_date

        # Save the updated job posting
        JobPosting.update(job_id, {
            'job_title': job_title,
            'status': status,
            'start_date': start_date,
            'end_date': end_date
        })

        return jsonify({'message': 'Job posting updated successfully'}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'message': 'Failed to update job posting', 'error': str(e)}), 500


@job_postings_routes.route('/other-job-postings', methods=['GET'])
def get_other_job_postings():
    # Get the token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        # Decode the token to get the user ID
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')

        # Fetch all job postings excluding those created by the user
        all_job_postings = JobPosting.find_all_except_user(user_id)

        # Format and return the job postings data
        job_postings_data = []
        for posting in all_job_postings:
            job_postings_data.append({
                '_id': str(posting['_id']),
                'job_title': posting['job_title'],
                'status': posting['status'],
                'start_date': str(posting['start_date']),
                'end_date': str(posting['end_date'])
            })

        return jsonify({'job_postings': job_postings_data}), 200

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'message': 'Failed to fetch job postings', 'error': str(e)}), 500


@job_postings_routes.route('/all-job-postings', methods=['GET'])
def get_all_job_postings():
    try:
        # Fetch all job postings from the database
        all_job_postings = JobPosting.find_all()

        # Format the job postings data
        job_postings_data = []
        for posting in all_job_postings:
            job_postings_data.append({
                '_id': str(posting['_id']),  # Convert ObjectId to string
                'job_title': posting['job_title'],
                'status': posting['status'],
                'start_date': str(posting['start_date']),
                'end_date': str(posting['end_date'])
            })

        return jsonify({'job_postings': job_postings_data}), 200

    except Exception as e:
        return jsonify({'message': 'Failed to fetch job postings', 'error': str(e)}), 500
