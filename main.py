from flask import Flask, render_template
from flask_restful import Api
import json


app = Flask(__name__, template_folder='frontend', static_url_path="/")
app.secret_key = 'SOME_KEY_qwertyuiop'
# api = Api(app)


@app.route('/')
def main():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
