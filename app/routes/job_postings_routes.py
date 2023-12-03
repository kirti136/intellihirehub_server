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
        print(start_date,end_date)

        # Check if all required fields are present
        if not all([job_title, status, start_date, end_date]):
            return jsonify({'message': 'Missing required fields'}), 400

       # Assuming start_date_str and end_date_str contain date strings in the format YYYY-MM-DD
        # start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        # end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

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
