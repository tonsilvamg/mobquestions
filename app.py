from flask import Flask, request, jsonify, redirect, g
from flask_pymongo import PyMongo

from werkzeug.security import generate_password_hash, check_password_hash

from bson import json_util

from config import MONGO_URI, MONGO_URI_TESTS, REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from auth import *

import os
import redis

rcache = redis.Redis(
            host=REDIS_HOST, 
            port=REDIS_PORT,
            password=REDIS_PASSWORD)


def create_app(testing = False):
    app = Flask(__name__)
    if os.getenv('FLASK_TESTING') and os.getenv('FLASK_TESTING')=="1":
        app.config['MONGO_URI'] = MONGO_URI_TESTS
    else:
        app.config['MONGO_URI'] = MONGO_URI
    app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
    app_context = app.app_context()
    app_context.push()        
    return app

mongo = None
app = create_app()
mongo = PyMongo(app)

col_users = mongo.db.users
col_questions = mongo.db.questions
col_tokens = mongo.db.tokens        # refresh tokens


def authenticate(username, password):
    user = col_users.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        return user
    else:
        return None

@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    user = authenticate(data['username'], data['password'])
    if user:
        token_payload = {'username': user['username']}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        col_tokens.insert_one({'value': refresh_token})
        return jsonify({'access_token': access_token, 
                        'refresh_token': refresh_token})
    else:
        return "Unauthorized", 401

@app.route('/', methods=['GET'])
@jwt_required
def index():
    res = col_users.find({})
    return json_util.dumps(list(res)), 200

@app.route('/cached_example', methods=['GET'])
def questao_mais_legal_cacheada():    
    if rcache and rcache.get('questao_legal'):
        return rcache.get('questao_legal'), 200
    else:
        question = col_questions.find({'id': 'c14ca8e5-b7'})
        if rcache:
            rcache.set('questao_legal', json_util.dumps(question))
    return json_util.dumps(question), 200

@app.route('/not_cached_example', methods=['GET'])
def questao_mais_legal():    
    question = col_questions.find({'id': 'bc3b3701-b7'})
    return json_util.dumps(question), 200


@app.route('/refresh_token', methods=['GET'])
@jwt_refresh_required
def refresh_token():    
    token = col_tokens.find_one({'value': g.token})
    if token:
        col_tokens.delete_one({'value': g.token})
        token_payload = {'username': g.parsed_token['username']}
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        col_tokens.insert_one({'value': refresh_token})
        return json_util.dumps({'access_token': access_token, 
                                'refresh_token': refresh_token}), 200
    else:
        return "Unauthorized", 401


# rota para visualizar o conteudo do payload encriptado no token.
@app.route('/token', methods=['GET'])
@jwt_required
def token():    
    return json_util.dumps(g.parsed_token), 200


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    if 'password' not in data.keys() or 'username' not in data.keys():
        return 'Dados insuficientes.', 400
    data['password'] = generate_password_hash(data['password'])
    col_users.insert_one(data)
    del(data['password'])
    return json_util.dumps(data), 201


@app.route('/users/<username>', methods=['GET'])
def get_user(username):
    return username, 200

# rota para exemplificar como utilizar obter variaveis
# de url. teste acessando 
# http://localhost:8088/questions/search?disciplina=1 
@app.route('/questions/search', methods=['GET'])
def search():
    disciplina = request.args.get('disciplina')
    return disciplina, 200

#----------------------------- 12/06/2018 -------------------------------------------------

# Atividade 19/06 - Questão 0
@app.route('/v1/users', methods=['POST'])
#@jwt_required
def jwt_cadastrar_usuario():
    data = request.get_json()
    usuario = col_users.find_one({"username": data['username'], "email": data['email']})
    if usuario:
        return 'Atividade 19/06 - Questão 0: usuario "' + usuario['username'] +  '" já exista na base de dados.', 203
    else:
        return 'Atividade 19/06 - Questão 0: usuario "' + data['username'] +  '" criado com sucesso.', 201

#---------------------------------------------
# Atividade 19/06 - Questão 1
@app.route('/v1/users/<username_url>', methods=['GET'])
def jwt_obter_usuario(username_url):
    encontrado = col_users.find_one({"username": username_url})
    if encontrado:
        return json_util.dumps(encontrado) , 200 # caso exista, retorne a coleção 
    else:
        return 'Atividade 19/06 - Questão 1: username:' + username_url + ' não encontrado!', 404 
     
#---------------------------------------------
# Atividade 19/06 - Questão 2
#POST /v1/authenticate (autenticação de usuário) valida a combinação username e password enviadas.
#  retorna status code 200 em caso de sucesso; e 403, caso a combinação seja inválida, e 400 caso não 
#  tenha sido enviados os dois valores: username e password. utilize-se a função check_password_hash
#  para comparar o password enviado com o password na base de dados da seguinte forma (por exemplo):
#  check_password_hash(password_encontrado, password_enviado). Esta função retorna True se houver 
# "correspondência". exemplo de dados de request:      
@app.route('/v1/authenticate', methods=['POST'])
#@jwt_required
def jwt_valida_usuario():
    data = request.get_json()
    if not 'username' in data.keys() or not 'password' in data.keys():
        return 'Atividade 19/06 - Questão 2: Erro=400, não enviou os dois valores.' , 400
    else:
        usuario = col_users.find_one({"username": data['username']})
        if usuario and check_password_hash(usuario['password'], data['password']):
            return 'Atividade 19/06 - Questão 2: usuario ' + usuario['username'] + ' autenticado.', 200
        else:
            return 'Atividade 19/06 - Questão 2: Erro=403, combinação usuário e senha é inválida!' , 403
        
#---------------------------------------------      
#Atividade 25/06 - Questão 3
#PUT /v1/users/ (atualização de dados de usuário) atualiza os dados do usuário correspondente (pelo username). 
#os campos possíveis de modificação são name; email e phones.
#{"name": "Markin", "phones": ["3333-2222"]}
@app.route('/v1/users', methods=['PUT'])
#@jwt_required
def atualiza_dados_put():
    data = request.get_json()

    if not "name" in data.keys() and not "email" in data.keys() and not "phones" in data.keys():
        return "Não atualizado! Informar name ou e-mail ou phones."

    sNome = ""
    sEmail = ""
    sPhones = [""]

    usuario = col_users.find_one({"username": data['username']})

    if "name" in data.keys(): sNome = data["name"]
    else: sNome = usuario["name"]

    if "email" in data.keys(): sEmail = data["email"]
    else: sEmail = usuario["email"]

    if "phones" in data.keys(): sPhones = data["phones"]
    else: sPhones = usuario["phones"]

    if usuario:
        col_users.update_one({"username":data['username']},{'$set': {'name':data["name"],'email':data["email"],'phones':data["phones"]} })
        return 'usuario ' + data['username'] + ' foi atualizado! ' , 201
    else:
        return 'usuario ' + data['username'] + ' não foi atualizado! ' + data['email'] + '-' + data['phones'] , 201


#---------------------------------------------      
# Atividade 12/06 - Questão 4
# PATCH /v1/users/ (redefinição de senha) modifica o password do usuário correspondente (pelo username). 
# exemplo de dados de request:
# {"password": "value"}
@app.route('/v1/users', methods=['PATCH'])
@jwt_required
def redefinir_senha():
    data = request.get_json()
    data['password'] = generate_password_hash(data['password'])
    col_users.update_one( {"username":g.parsed_token['username']},{"$set":{"password":data['password']}} )
    return g.parsed_token['username'] + ", a senha alterada com sucesso Valew!", 200

#---------------------------------------------      
# Atividade 25/06 - Questão 5
# GET /v1/questions/<question_id> (obtenção de questão) retorna os dados da questão correpondente (pelo username) 
# em formato JSON e o status code 200; ou status code 404 caso a questão não exista.
@app.route('/v1/questions/<id_url>', methods=['GET'])
def obter_questao(id_url):
    encontrado = col_questions.find_one({"id":id_url})
    if encontrado:
        return json_util.dumps(encontrado), 200
    else:
        return "Não encontrado.",404

#---------------------------------------------      
# Atividade 25/06 - Questão 6
# POST /v1/questions/<question_id>/comment (incluir comentário em questão) retorna os dados da questão 
# atualizada em formato json e o status code 200 em caso de sucesso. se a questão não for encontrada, 
# status code 404. se o usuário não for encontrado, ou os dados enviados estiverem inválidos retornar 
# status code 400.
# {"username": "mark", "message": "essa questao e facil"}
#@app.route('/v1/questions/<id_url>/comment', methods=['GET'])
#def obter_questao2(id_url):
#    encontrado = col_questions.find_one({"id":id_url})
#    if encontrado:
#        return json_util.dumps(encontrado), 200
#    else:
#        return "Não encontrado.",404    