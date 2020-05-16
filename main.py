# Main app file. It connects API to the app


from flask import Flask, render_template, request, session, redirect, url_for
from flask_restful import Api
import json
from sys import path
from data import auth, dial
from waitress import serve


app = Flask(__name__, template_folder='frontend', static_url_path="/")
app.secret_key = "QWERTYUIOP23456789"
api = Api(app)


# Page which introduces user to the app
@app.route('/')
def main():
    return render_template("index.html")


# Page where you can log in
@app.route('/login')
def login():
    return render_template("login.html")


# Page where user registser their accounts
@app.route('/registration')  # Try to type it yourself
def registration():
    return render_template("registration.html")


# Page with all of your chats
@app.route('/chats')
def chats():
    if 'logged_in' not in list(session.keys()):
        return render_template('logout.html')
    return render_template("chats.html")


# Page with concrete chat
@app.route('/chat/<int:cid>')
def chat(cid):
    if 'logged_in' not in session.keys():
        return render_template('logout.html')
    return render_template("chat.html", cid=cid)


# Empty page, where user logs out
@app.route('/logout')
def logout():
    return render_template('logout.html')


# all API resources
api.add_resource(auth.AuthResource, '/api/auth')
api.add_resource(dial.ChatsResource, '/api/chats')
api.add_resource(dial.UserInfoResource, '/api/users')
api.add_resource(dial.MessageResource, '/api/messages')
api.add_resource(dial.DialogResource, '/api/dialogs')
api.add_resource(dial.SelfResource, '/api/self')
api.add_resource(dial.HostedDialogResource, '/api/hosted')
api.add_resource(dial.PicturesResource, '/api/pictures')
api.add_resource(dial.FilesResource, '/api/files')

if __name__ == '__main__':
    # app.run(port=8080, host='0.0.0.0', debug=True)
    serve(app, host='0.0.0.0', port=8080)