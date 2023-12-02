from app import app

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask,jsonify
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# @app.route('/')
# def welcome():
#     return jsonify({'message': 'Welcome to the IntelliHireHub-Server'})

# if __name__ == '__main__':
#     app.run(debug=True)
