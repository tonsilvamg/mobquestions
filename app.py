from flask import Flask, jsonify, redirect
from flask_pymongo import PyMongo

app = Flask('du2x')
mongo = PyMongo(app)


@app.route('/')
def index():
    users = mongo.db.users.find({})
    return jsonify(list(users))

@app.route('/create/')
def create(mongodb):
    mongo.db.users.insert({'a': 1, 'b': 2})
    redirect("/")


app.run()