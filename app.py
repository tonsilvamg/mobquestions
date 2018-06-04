from flask import Flask, jsonify, redirect
from flask_pymongo import PyMongo

from bson import json_util

from config import *


app = Flask(__name__)
mongo = PyMongo(app)

@app.route('/')
def index():
    res = mongo.db.stuff.find({})
    return json_util.dumps(list(res))

@app.route('/create/<name>')
def create(name):
    mongo.db.stuff.insert({'username': name})
    return redirect("/")

app.run(host='0.0.0.0', debug=True)
