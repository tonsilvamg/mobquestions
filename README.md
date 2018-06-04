# mobquestions
Repositório de atividades para disciplina de arquitetura de computação em nuvens


## Pré-requisitos

1. Clonar este repositório. Se necessário, instale o Git for windows disponível em: https://git-scm.com/download/win. Para clonar, rode o comando: 
```sh
git clone https://github.com/du2x/mobquestions
```
2. Instalar python (gerenciador de pacotes): https://python.org. Caso esteja utilizando Windows, instalar como Administrador e marcar as duas opções conforme a imagem: https://djangobook.com/wp-content/uploads/figure1_1a.png. 
3. Instale o `pymongo` (driver de mongo para o python). Execute no prompt de comando: `python -m pip install pymongo`
4. Criar conta, instência de base de dados e usuário em https://mlab.com.
5. Criar coleção `questions` e importar nesta coleção o arquivo -> https://goo.gl/AafJqP.
6. Vamos agora testar a conexão com a conta no mlab com o pymongo: 
```python
connection = pymongo.MongoClient(ds043358.mlab.com, 43358)
db = connection['ubiqs']
db.authenticate(auser, 'a123456')
```

