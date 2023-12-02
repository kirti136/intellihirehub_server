from flask import Flask, jsonify
from flask_cors import CORS
from app.routes.user_routes import user_routes

app = Flask(__name__)
CORS(app)


@app.route('/')
def welcome():
    return jsonify({'message': 'Welcome to the IntelliHireHub-Server'})


app.register_blueprint(user_routes)
