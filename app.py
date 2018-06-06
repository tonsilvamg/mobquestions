from flask import Flask, request, jsonify, redirect
from flask_pymongo import PyMongo

from werkzeug.security import generate_password_hash, check_password_hash

from bson import json_util

from config import MONGO_URI

app = Flask(__name__)
app.config['MONGO_URI'] = MONGO_URI
app.config['DEBUG'] = True

app_context = app.app_context()
app_context.push()

mongo = PyMongo(app)

col_users = mongo.db.users
col_questions = mongo.db.questions

@app.route('/', methods=['GET'])
def index():
    res = col_users.find({})
    return json_util.dumps(list(res)), 201

@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    data['password'] = generate_password_hash(data['password'])
    col_users.insert_one(data)
    return 'usuario ' + data['username'] + ' criado.', 201

@app.route('/users', methods=['PUT'])
def create_user_put():
    data = request.get_json()
    data['password'] = generate_password_hash(data['password'])
    col_users.insert_one(data)
    return 'usuario ' + data['username'] + ' criado.', 201

@app.route('/users/<username_url>', methods=['POST'])
def get_user_POST(username_url):
    encontrado = col_users.find_one({'username':username_url}) 
    if not encontrado: 
      return username_url + ' não existe!', 203
    else:
      return username_url + ' já está criado!' , 201 # caso o usuário seja criado

@app.route('/users/<username_url>', methods=['GET'])
def get_user_GET(username_url):
    encontrado = col_users.find_one({'username':username_url}) 
    if not encontrado: 
      return 'Não encontrado!', 404
    else:
      return json_util.dumps(encontrado) , 200 # caso o usuário seja criado
          

# rota para exemplificar como utilizar obter variaveis
# de url. teste acessando 
# http://localhost:8088/questions/search?disciplina=BancoDeDados 
@app.route('/questions/search', methods=['GET'])
def search():
    disciplina = request.args.get('disciplina')
    return disciplina, 200
