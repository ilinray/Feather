from flask import Flask, render_template, request, session
from flask_restful import Api
import json
from sys import path
from data import auth
# from data.db_funcs import UserConnector

path.append(path[0] + '\\data')

app = Flask(__name__, template_folder='frontend', static_url_path="/")
app.secret_key = "QWERTYUIOP23456789"
api = Api(app)


@app.route('/')
def main():
    return render_template("index.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/registration')
def registration():
    return render_template("registration.html")

@app.route('/chat')
def registration():
    return render_template("chat.html")
    
api.add_resource(auth.AuthResource, '/api/auth')

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
