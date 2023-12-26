from flask import Flask, render_template, jsonify, request
from src import functions
import mysql.connector

# 全局变量
Ewallet = Flask(__name__)       # 服务器名称
connect = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='Cp20031212',
    database='lab8'
)                               # 当前连接
user_id = None                  # 当前账户id
user_type = False               # 当前用户类型

# 主页
@Ewallet.route('/')
def home():
    global connect
    connect = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='Cp20031212',
        database='lab8'
    )
    return render_template("denglu.html")

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

# 修改密码界面
@Ewallet.route('/shuaxin')
def shuaxin():
    global connect
    connect = mysql.connector.connect(
        host='localhost',
        user='root',
        passwd='Cp20031212',
        database='lab8'
    )
    return render_template("shuaxin.html")

# 登录
@Ewallet.route('/denglu', methods = ["POST"])
def denglu():
    global connect, user_id, user_type
    info = request.get_json()
    user = info["username_"]
    psd = info["pass_"]
    # 获取登录信息

    ret = ""
    # 尝试登录
    ret = functions.login(user, psd, connect)

    if ret == "success":
        # 登录成功，配置登录信息
        user_type, _ = functions.get_account_type(user, connect)
        if user_type:
            # 经理连接
            connect = mysql.connector.connect(
                host = 'localhost',
                user = 'manager',
                passwd = '12345678',
                database = 'lab8'
            )
            ret = "2"
        else:
            # 客户连接
            connect = mysql.connector.connect(
                host = 'localhost',
                user = 'cust',
                passwd = '87654321',
                database = 'lab8'
            )
            ret = "1"
    return jsonify(ret)

# 获取验证码
@Ewallet.route('/getcode', methods = ["POST"])
def getcode():
    global connect
    phone = request.get_json()
    phone = phone["ponum_"]
    if not functions.legal_phone(phone):
        return jsonify("手机号格式不正确，请检查。")
    else:
        functions.create_code(phone, connect)
        return jsonify("验证码已发送。")

# 修改密码
@Ewallet.route('/xiugaimima', methods = ["POST"])
def xiugaimima():
    global connect
    # post了新密码、手机号、验证码，需要返回true/false
    info = request.get_json()
    account = info["username_"]
    psd = info["pass_"]
    phone = info["ponum_"]
    code  = info["code_"]
    ret = ""
    
    note = functions.verify_code(phone, code, connect)
    if note != "1":
        ret = note
    else:
        account_info = functions.get_account_infomation(account, connect)
        # 判断账户是否存在
        if account_info is None:
            ret = "账户不存在"
        # 判断手机号是否匹配
        elif len(psd) < 6:
            ret = "密码小于6位，请重新设置。"
        elif phone != account_info[0]:
            ret = "手机号、账号不匹配。"
        # 修改密码
        else:
            functions.change_psd(account, psd, connect)
            ret = "1"
    return jsonify(ret)

# 客户界面信息申请
@Ewallet.route('/kehuid_post', methods = ["POST"])
def kehuid_post():
    global connect, user_id
    # post了账号，需要返回姓名，客户id，余额，限额
    account = request.get_json()["kehuid_"]
    ret = {"flag": True, "info":""}
    ret["dota"] = functions.get_cust_info(account, connect)
    user_id = ret["dota"][1]
    return jsonify(ret)

# 存钱
@Ewallet.route('/cunqian', methods = ["POST"])
def cunqian():
    global connect, user_id
    # post了账号,金额，密码，需要返回：”1“（成功）、错误信息（失败）
    ret = {"flag": False, "info": ""}
    info = request.get_json()
    account = info["kehuuser"]
    amount = info["amount"]
    psd = info["pass"]

    ans_psd = functions.get_account_infomation(account, connect)
    if ans_psd[1] != psd:
        ret["info"] = "密码错误，请重新输入。"
    else:
        ans = functions.initiate_transaction(0, account, amount, connect)
        if ans == "1":
            ret["flag"] = True
            ret["info"] = "存入成功，余额已变更，请尝试刷新。"
        else:
            ret["info"] = ans

    return jsonify(ret)

# 取钱
@Ewallet.route('/quqian', methods = ["POST"])
def quqian():
    global connect, user_id
    # post了账号,金额，密码，需要返回：”1“（成功）、错误信息（失败）
    ret = {"flag": False, "info": ""}
    info = request.get_json()
    account = info["kehuuser"]
    amount = info["amount"]
    psd = info["pass"]

    ans_psd = functions.get_account_infomation(account, connect)
    if ans_psd[1] != psd:
        ret["info"] = "密码错误，请重新输入。"
    else:
        ans = functions.initiate_transaction(account, 0, amount, connect)
        if ans == "1":
            ret["flag"] = True
            ret["info"] = "成功取出，余额已变更，请尝试刷新。"
        else:
            ret["info"] = ans

    return jsonify(ret)

# 转账
@Ewallet.route('/zhuan', methods = ["POST"])
def zhuan():
    global connect, user_id
    # post了转入账号，转出账号，金额，密码，需要返回：”1“（成功）、错误信息（失败）
    ret = {"flag": False, "info": ""}
    info = request.get_json()
    account = info["kehuuser"]
    amount = info["amount"]
    psd = info["pass"]
    account_b = info["targetuser"]

    ans_psd = functions.get_account_infomation(account, connect)
    if ans_psd[1] != psd:
        ret["info"] = "密码错误，请重新输入。"
    else:
        ans = functions.initiate_transaction(account, account_b, amount, connect)
        if ans == "1":
            ret["flag"] = True
            ret["info"] = "交易发起成功，等待对方确认。"
        else:
            ret["info"] = ans

    return jsonify(ret)

# 客户查询
@Ewallet.route('/kehusearch', methods = ["POST"])
def kehusearch():
    global connect, user_id
    # post了客户账号，需要返回：该客户的交易记录（成功）、错误信息（失败）
    # account = request.get_json()["kehuuser"]
    return jsonify(functions.get_pending_transactions(user_id, connect))

# 撤销交易
@Ewallet.route('/chexiao', methods = ["POST"])
def chexiao():
    global connect, user_id
    # post了交易ID，返回"1"（成功），错误信息（失败）
    ret = {"flag": False, "info": ""}
    trade_id = request.get_json()
    trade_id = trade_id["jiaoyiid"]
    print(type(trade_id), trade_id)
    ans = functions.modify_transaction(user_id, trade_id, 3, connect)
    if ans == "1":
        ret["flag"] = True
        ret["info"] = "操作成功，刷新页面后显示操作结果。"
    else:
        ret["info"] = ans
    return jsonify(ret)

# 确认付款
@Ewallet.route('/jieshou', methods = ["POST"])
def jieshou():
    global connect, user_id
    # post了交易ID，返回"1"（成功），错误信息（失败）
    ret = {"flag": False, "info": ""}
    trade_id = request.get_json()
    trade_id = trade_id["jiaoyiid"]
    print(type(trade_id), trade_id)
    ans = functions.modify_transaction(user_id, trade_id, 1, connect)
    if ans == "1":
        ret["flag"] = True
        ret["info"] = "操作成功，刷新页面后显示操作结果。"
    else:
        ret["info"] = ans
    return jsonify(ret)

# 拒绝接受
@Ewallet.route('/jujue', methods = ["POST"])
def jujue():
    global connect, user_id
    # post了交易ID，返回"1"（成功），错误信息（失败）
    ret = {"flag": False, "info": ""}
    trade_id = request.get_json()
    trade_id = trade_id["jiaoyiid"]
    print(type(trade_id), trade_id)
    ans = functions.modify_transaction(user_id, trade_id, 2, connect)
    if ans == "1":
        ret["flag"] = True
        ret["info"] = "操作成功，刷新页面后显示操作结果。"
    else:
        ret["info"] = ans
    return jsonify(ret)

# 经理界面信息申请
@Ewallet.route('/jlid_post', methods = ["POST"])
def jlid_post():
    global connect, user_id
    # post了经理账号，需要返回经理姓名，本月流水
    account = request.get_json()["jlid_"]
    ret = {}
    info = functions.get_manager_info(account, connect)
    user_id = info[1]
    ret["name"] = info[0]
    ret["liushui"] = functions.get_transactions(connect)
    return jsonify(ret)

# 开户
@Ewallet.route('/kaihu', methods = ["POST"])
def kaihu():
    global connect
    # post了经理账号，新客户账号，新客户密码，确认密码，手机号，姓名，需要返回：”1“（成功）、错误信息（失败）
    # 获取开户信息
    info = request.get_json()
    old_psd = info["newkehupass_"]
    new_psd = info["querenpass_"]
    phone = info["phonenum_"]
    name = info["kehuname_"]
    
    ret = {}
    ret["flag"] = False
    ret["info"] = ""
    # 尝试开户
    if not functions.legal_phone(phone):
        ret["info"] = "手机号格式不正确，请检查。"
    elif len(name) > 20:
        ret["info"] = "姓名长度不能超过20，请重新设置。"
    elif len(old_psd) < 6 or len(old_psd) > 20:
        ret["info"] = "密码长度应在6-20之间，请重新输入。"
    elif old_psd != new_psd:
        ret["info"] = "两次输入的密码不一致，请重新输入。"
    else:
        new_id, _ = functions.create_account(name, phone, old_psd, connect)
        ret["flag"] = True
        ret["info"] = f'创建成功，新账号为“{new_id}”，请小心保存。'
    
    return jsonify(ret)

# 销户
@Ewallet.route('/xiaohu', methods = ["POST"])
def xiaohu():
    global connect
    # post了客户账号，经理账号，需要返回：”1“（成功）、错误信息（失败）
    accunt = request.get_json()["kehuuser_"]
    return jsonify(functions.delete_cust(accunt, connect))
    # 销户只会消除账号，不会消除客户信息、交易、交易记录。

# 升级
@Ewallet.route('/shengji', methods = ["POST"])
def shengji():
    global connect
    # post了客户账号，经理账号，提升额度，需要返回：”1“（成功）、错误信息（失败）
    info = request.get_json()
    account = info["kehuuser_"]
    amount = info["level_"]
    return jsonify(functions.update_limit(account, amount, connect))

# 经理查询
@Ewallet.route('/jlsearch', methods = ["POST"])
def jlsearch():
    global connect
    # post了客户账号，经理账号，需要返回：该客户的交易记录（成功）、错误信息（失败）
    account = request.get_json()["kehuuser_"]
    return jsonify(functions.get_customer_transactions(account, connect))

if __name__ == '__main__':
    Ewallet.run(debug=True)