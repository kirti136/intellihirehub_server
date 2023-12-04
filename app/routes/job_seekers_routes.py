from flask import Blueprint, request, jsonify
from app.models.job_seekers import JobSeekerProfile
import jwt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the JWT secret key from environment variables
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

job_seeker_profile_routes = Blueprint('job_seeker_profile_routes', __name__)


@job_seeker_profile_routes.route('/create-job-seeker-profile', methods=['POST'])
def create_job_seeker_profile():
    data = request.get_json()

    # Get the token from the request headers
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 401

    try:
        # Decode the token to get the user ID
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')

        name = data.get('name')
        status = data.get('status')
        skills = data.get('skills')
        experience = data.get('experience')
        bio = data.get('bio')
        availability = data.get('availability')

        # Check if all required fields are present
        if not all([name, status, skills, experience, bio, availability]):
            return jsonify({'message': 'Missing required fields'}), 400

        # Create a new JobSeekerProfile instance with the extracted data
        new_profile = JobSeekerProfile(
            user_id=user_id,
            name=name,
            status=status,
            skills=skills,
            experience=experience,
            bio=bio,
            availability=availability
        )

        # Save the job seeker profile
        new_profile.save()

        return jsonify({'message': 'Job Seeker profile created successfully'}), 201

    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'message': 'Failed to create job seeker profile', 'error': str(e)}), 500
