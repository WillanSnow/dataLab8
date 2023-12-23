from flask import Flask, render_template, jsonify
# from test import test
# from support import test

Ewallet = Flask(__name__)

@Ewallet.route('/')
def home():
    return render_template("denglu.html")

@Ewallet.route('/get_message', methods=['GET'])
def get_message():
    message = "ni ma si le"
    return jsonify(message)

@Ewallet.route('/shuaxin')
def shuaxin():
    return render_template("shuaxin.html")

if __name__ == '__main__':
    Ewallet.run(debug=True)