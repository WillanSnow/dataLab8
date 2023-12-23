from flask import Flask, render_template, jsonify, request

Ewallet = Flask(__name__)

# 主页
@Ewallet.route('/')
def home():
    return render_template("home.html")

# 用户页
@Ewallet.route('/customer')
def cust():
    return render_template("cust.html")

# 经理页
@Ewallet.route('/manager')
def manager():
    return render_template("manager.html")

# 登录post请求
@Ewallet.route('/login', methods = ['POST'])
def try_to_login():
    name = request.form.get('username')
    psd = request.form.get("password")
    # 用户名为空
    if name is None:
        return "用户名不能为空"
    # 密码为空
    if psd is None:
        return "密码不能为空"
    
    # 登录成功，直接跳转
    # if support.login(psd, name):
    #     return "登录成功"
    # else:
    return "登录失败"

@Ewallet.route('/sendMessage', methods = ["POST"])
def sendMessage():
    print('ni ma si le')
    print(request.get_json()["testitem"])
    return jsonify("nihao")

if __name__ == '__main__':
    Ewallet.run(debug=True)