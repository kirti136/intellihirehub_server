from app.database import get_database
from bson import ObjectId


class JobPosting:
    def __init__(self, job_title, status, start_date, end_date=None, hiring_manager_id=None):
        self.job_title = job_title
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.hiring_manager_id = hiring_manager_id

    def save(self):
        db = get_database()
        collection = db['job_postings']  # Assuming 'job_postings' is the collection name
        job_data = {
            'job_title': self.job_title,
            'status': self.status,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'hiring_manager_id': self.hiring_manager_id
        }
        collection.insert_one(job_data)

    @staticmethod
    def find_by_id(job_id):
        db = get_database()
        collection = db['job_postings']
        return collection.find_one({'_id': ObjectId(job_id)})

    @staticmethod
    def update(job_id, updated_data):
        db = get_database()
        collection = db['job_postings']

        query = {'_id': ObjectId(job_id)}
        new_values = {'$set': updated_data}

        collection.update_one(query, new_values)

    @staticmethod
    def find_by_hiring_manager(hiring_manager_id):
        db = get_database()
        collection = db['job_postings']
        return collection.find({'hiring_manager_id': hiring_manager_id})
