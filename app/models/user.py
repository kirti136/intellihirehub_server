from app.database import get_database


class User:
    def __init__(self, name, email, password, role):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def save(self):
        db = get_database()
        collection = db['users']  # Assuming 'users' is the collection name
        user_data = {
            'name': self.name,
            'email': self.email,
            'password': self.password,
            'role': self.role
        }
        collection.insert_one(user_data)

    @staticmethod
    def find_by_email(email):
        db = get_database()
        collection = db['users']  # Assuming 'users' is the collection name
        return collection.find_one({'email': email})
