from app.database import get_database
from bson import ObjectId


class JobSeekerProfile:
    def __init__(self, user_id, name, status, skills, experience, bio, availability):
        self.user_id = user_id
        self.name = name
        self.status = status
        self.skills = skills
        self.experience = experience
        self.bio = bio
        self.availability = availability

    def save(self):
        db = get_database()
        collection = db['job_seeker_profiles']
        profile_data = {
            'user_id': self.user_id,
            'name': self.name,
            'status': self.status,
            'skills': self.skills,
            'experience': self.experience,
            'bio': self.bio,
            'availability': self.availability
        }
        collection.insert_one(profile_data)

    @staticmethod
    def find_by_id(profile_id):
        db = get_database()
        collection = db['job_seeker_profiles']
        return collection.find_one({'_id': ObjectId(profile_id)})

    @staticmethod
    def update(profile_id, updated_data):
        db = get_database()
        collection = db['job_seeker_profiles']

        query = {'_id': ObjectId(profile_id)}
        new_values = {'$set': updated_data}

        collection.update_one(query, new_values)

    @staticmethod
    def delete(profile_id):
        db = get_database()
        collection = db['job_seeker_profiles']
        collection.delete_one({'_id': ObjectId(profile_id)})

    @staticmethod
    def find_all():
        db = get_database()
        collection = db['job_seeker_profiles']
        return collection.find()
