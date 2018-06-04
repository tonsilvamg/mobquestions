from flask import Flask, jsonify, redirect
from flask_pymongo import PyMongo

from config import *


app = Flask('du2x')
mongo = PyMongo(app)


@app.route('/')
def index():
    res = mongo.db.stuff.find({})
    return jsonify(list(res))

@app.route('/create/')
def create(mongodb):
    mongo.db.stuff.insert({'a': 1, 'b': 2})
    redirect("/")

app.run(host='0.0.0.0', debug=True)
