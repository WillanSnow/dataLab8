from flask import Flask, render_template, jsonify, request

Ewallet = Flask(__name__)

# 主页
@Ewallet.route('/')
def home():
    return render_template("denglu.html")

# 修改密码界面
@Ewallet.route('/shuaxin')
def shuaxin():
    return render_template("shuaxin.html")

# 客户页
@Ewallet.route('/kehu')
def kehu():
    kehuid_ = request.args.get("kehuid")
    return render_template("kehu.html",kehuid=kehuid_)

# 经理页
@Ewallet.route('/jingli')
def jingli():
    jlid_ = request.args.get("jlid")
    return render_template("jingli.html",jlid=jlid_)

# 登录
@Ewallet.route('/denglu', methods = ["POST"])
def denglu():
    # post了账号，密码， 如果成功，返回”1“（客户），”2“（经理），否则返回错误信息
    return jsonify("2")

# 修改密码
@Ewallet.route('/xiugaimima', methods = ["POST"])
def xiugaimima():
    # post了账号、新密码、手机号、验证码，如果成功，返回”1“，否则返回错误信息。
    return jsonify("1")

# 客户界面信息申请
@Ewallet.route('/kehuid_post', methods = ["POST"])
def kehuid_post():
    # post了账号，需要返回姓名，客户id，余额，限额
    return jsonify("1")

# 存钱
@Ewallet.route('/cunqian', methods = ["POST"])
def cunqian():
    # post了账号,金额，密码，需要返回：”1“（成功）、错误信息（失败）
    return jsonify("1")

# 取钱
@Ewallet.route('/quqian', methods = ["POST"])
def quqian():
    # post了账号,金额，密码，需要返回：”1“（成功）、错误信息（失败）
    return jsonify("1")

# 转账
@Ewallet.route('/zhuan', methods = ["POST"])
def zhuan():
    # post了转入账号，转出账号，金额，密码，需要返回：”1“（成功）、错误信息（失败）
    return jsonify("1")

# 客户查询
@Ewallet.route('/kehusearch', methods = ["POST"])
def kehusearch():
    # post了客户账号，需要返回：该客户的交易记录（成功）、错误信息（失败）
    return jsonify("1")

# 经理界面信息申请
@Ewallet.route('/jlid_post', methods = ["POST"])
def jlid_post():
    # post了经理账号，需要返回经理姓名，本月流水
    return jsonify("1")

# 开户
@Ewallet.route('/kaihu', methods = ["POST"])
def kaihu():
    # post了经理账号，新客户账号，新客户密码，确认密码，手机号，姓名，需要返回：”1“（成功）、错误信息（失败）
    return jsonify("1")

# 销户
@Ewallet.route('/xiaohu', methods = ["POST"])
def xiaohu():
    # post了客户账号，经理账号，需要返回：”1“（成功）、错误信息（失败）
    return jsonify("1")

# 升级
@Ewallet.route('/shengji', methods = ["POST"])
def shengji():
    # post了客户账号，经理账号，提升额度，需要返回：”1“（成功）、错误信息（失败）
    return jsonify("1")

# 经理查询
@Ewallet.route('/jlsearch', methods = ["POST"])
def jlsearch():
    # post了客户账号，经理账号，需要返回：该客户的交易记录（成功）、错误信息（失败）
    return jsonify("1")

if __name__ == '__main__':
    Ewallet.run(debug=True)