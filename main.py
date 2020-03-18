from flask import Flask, render_template
from flask_restful import Api
import json


app = Flask(__name__, template_folder='frontend', static_url_path="/")
# api = Api(app)


@app.route('/')
def main():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
