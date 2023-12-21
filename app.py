from flask import Flask, render_template, jsonify
from test import test
from flask import request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/get_message', methods=['GET'])
def get_message():
    message = test()
    return jsonify({'message': message})

if __name__ == '__main__':
    app.run(debug=True)