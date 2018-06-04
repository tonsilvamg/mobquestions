from flask import Flask, request, jsonify, redirect
from flask_pymongo import PyMongo

from werkzeug.security import generate_password_hash, check_password_hash

from bson import json_util

from config import *

app = Flask(__name__)
app_context = app.app_context()
app_context.push()

mongo = PyMongo(app)

col_users = mongo.db.users
col_questions = mongo.db.questions

@app.route('/', methods=['GET'])
def index():
    res = mongo.db.stuff.find({})
    return json_util.dumps(list(res))

@app.route('/user/', methods=['POST'])
def create_user():
    data = request.get_json(silent=True)
    data['password'] = generate_password_hash(data['password'])
    col_users.insert_one(data)
    return redirect("/")
