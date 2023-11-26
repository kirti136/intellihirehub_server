# app.py

from flask import Flask
from flask_cors import CORS
from .user_routes import user_routes

app = Flask(__name__)
CORS(app)
app.register_blueprint(user_routes)

@app.route('/')
def welcome():
    return jsonify({'message': 'Welcome to the IntelliHireHub-Server'})

if __name__ == '__main__':
    app.run(debug=True)
