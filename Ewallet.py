from flask import Flask, render_template, jsonify
# from test import test
import pymysql
from support import test

Ewallet = Flask(__name__)

@Ewallet.route('/')
def home():
    return render_template("home.html")

@Ewallet.route('/get_message', methods=['GET'])
def get_message():
    message = test()
    return jsonify(message)

@Ewallet.route('/login')
def login():
    return render_template("login.html")

if __name__ == '__main__':
    Ewallet.run(debug=True)