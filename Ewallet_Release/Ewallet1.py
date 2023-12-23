from flask import Flask, render_template, jsonify, request
from src.support import *

Ewallet = Flask(__name__)

# 主页
@Ewallet.route('/')
def home():
    return render_template("denglu.html")

# 修改密码界面
@Ewallet.route('/shuaxin')
def shuaxin():
    return render_template("shuaxin.html")

# 用户页
@Ewallet.route('/kehu')
def kehu():
    kehuid_ = request.args.get("kehuid")
    return render_template("kehu.html",kehuid=kehuid_)

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

@Ewallet.route('/xiugaimima', methods = ["POST"])
def xiugaimima():
    # post了新密码、手机号、验证码，需要返回true/false
    phone = request.get_json("ponum_")
    code = request.get_json("code_")
    psd = request.get_json("pass_")
    
    if not legal_phone(phone):
        ret = "手机号格式不正确，请检查"
    elif not legal_code(code) or code != phone[11-4: ]:
        ret = "验证码不正确，请重新输入"
    else:

        ret = 1
    return jsonify(ret)

@Ewallet.route('/denglu', methods = ["POST"])
def denglu():
    return jsonify("1")

if __name__ == '__main__':
    connectot = None
    
    Ewallet.run(debug=True)