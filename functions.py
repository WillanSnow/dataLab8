## This file contains all the functions used in the project.
## You need to install this library, you can use pip to install pip install mysql-connector-python
## including tables: trade,customer,change_trade,account,manager
## table :
# - account：
#   - 账号：标识码，创建账户时，需要随机生成8位数。account_id（int）
#   - 密码：10字符以内的字符串 password(string)
#   - 手机号：固定长度为11的一串数字 phone_num(string)
# - 客户：
#   - 客户id：5位数字标识码，随机生成或累计的形式。cust_id(int)
#   - 姓名：客户的名字    name(string)
#   - 余额：账户余额，发起交易时，直接扣除；接收交易时，才增加到目标用户；拒绝交易时，金额回到发起客户余额。balance(float)
#   - 限额：单笔交易的限额。limit(float)
# - 交易：
#   - 交易id：15位数字标识码；trade_id(int)
#   - 金额：交易的额度 amount(float)
#   - 状态：整数，0~3，依次表示：待确认、已完成、未成功(接受者取消或发起者撤销)、数据错误(debug或测试用)。status(int)
#   - cust_a：交易发起客户，存钱时为“system”，取钱时为对应客户；cust_a(int)
#   - cust_b：交易接收客户，存钱时为对应客户，取钱时为“system”。 cust_b(int)
# - change(客户修改交易状态的记录)：
#   - change_id(int)
#   - change_time：修改时间 date
#   - 交易id：被修改的交易 trade_id(int)
#   - cust_id：客户id cust_id(int)
#   - 修改内容：整数0-4，依次对应：发起交易、接收交易、拒绝交易、撤销交易、数据错误。action(int)
import random
import mysql.connector
from datetime import datetime, timedelta

# 
def login(account, password):
    """
    登录函数：给定account、password，返回登录结果（-1：登录失败，账号不存在；0：登录失败，密码错误；1：登录成功）

    参数：
    - account：账号
    - password：密码
    
    返回：
    - 登录结果：-1：登录失败，账号不存在；0：登录失败，密码错误；1：登录成功
    """
    conn = mysql.connector.connect(
        host='localhost',  # 数据库主机地址
        user='your_username',  # 数据库用户名
        passwd='your_password',  # 数据库密码
        database='your_database'  # 数据库名
    )
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM account WHERE account_id =%s", (account,))
    result = cursor.fetchone()

    if result is None:
        return -1  # 账号不存在
    elif result[0] != password:
        return 0  # 密码错误
    else:
        return 1  # 登录成功


def get_pending_transactions(account):
    """
    消息提醒函数：给定account，返回等待其确认的交易(即发给他且他未确认的交易)

    参数：
    - account：账号

    返回：
    - 等待确认的交易：(trade_id, amount, status, cust_a, cust_b)
    """
    conn = mysql.connector.connect(
        host='localhost',  # 数据库主机地址
        user='your_username',  # 数据库用户名
        passwd='your_password',  # 数据库密码
        database='your_database'  # 数据库名
    )
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trade WHERE cust_b=%s AND status=0", (account,))
    result = cursor.fetchall()

    return result


def initiate_transaction(cust_a, cust_b, amount):
    """
    交易发起函数：给定发起客户、目标客户、金额，若目标客户不存在，金额超过发起客户单笔额度，交易发起失败，返回失败信息；否则发起成功，创建交易(注意创建交易、change元组)。
    注意：存、取、交易都是通过这个函数实现的，存由‘系统’账户发起，客户接收；取由客户发起，‘系统’接收。

    参数：
    - cust_a：发起客户
    - cust_b：目标客户
    - amount：金额

    返回：
    - 交易发起结果：交易发起成功/失败信息
    """
    conn = mysql.connector.connect(
        host='localhost',  # 数据库主机地址
        user='your_username',  # 数据库用户名
        passwd='your_password',  # 数据库密码
        database='your_database'  # 数据库名
    )
    cursor = conn.cursor()

    # 检查目标客户是否存在
    cursor.execute("SELECT * FROM customer WHERE cust_id=%s", (cust_b,))
    if cursor.fetchone() is None:
        return "目标客户不存在"

    # 检查金额是否超过发起客户的单笔限额
    cursor.execute("SELECT limit FROM customer WHERE cust_id=%s", (cust_a,))
    limit = cursor.fetchone()[0]
    if amount > limit:
        return "金额超过发起客户单笔限额"

    # 创建交易记录
    trade_id = generate_id()  
    cursor.execute(
        "INSERT INTO trade (trade_id, amount, status, cust_a, cust_b) VALUES (%s, %s, 0, %s, %s)",
        (trade_id, amount, cust_a, cust_b)
    )

    # 创建change记录
    change_id = generate_id()  
    change_time = datetime.now()
    cursor.execute(
        "INSERT INTO change (change_id, change_time, trade_id, cust_id, action) VALUES (%s, %s, %s, %s, 0)",
        (change_id, change_time, trade_id, cust_a)
    )

    conn.commit()

    return "交易发起成功"


def modify_transaction(cust_id, trade_id, action):
    """
    修改交易：给定客户、交易、操作(接收、撤销、拒绝)，修改数据库对应信息(注意同步余额、trade状态，增加change条目)

    参数：
    - cust_id：客户
    - trade_id：交易
    - action：操作(接收、撤销、拒绝)

    返回：
    - 交易修改结果：交易修改成功/失败信息
    """
    conn = mysql.connector.connect(
        host='localhost',  # 数据库主机地址
        user='your_username',  # 数据库用户名
        passwd='your_password',  # 数据库密码
        database='your_database'  # 数据库名
    )
    cursor = conn.cursor()

    # 获取交易信息
    cursor.execute("SELECT * FROM trade WHERE trade_id=%s", (trade_id,))
    trade = cursor.fetchone()
    if trade is None:
        return "交易不存在"

    # 检查操作是否合法
    if action not in [0, 1, 2, 3, 4]:
        return "操作不合法"

    # 更新交易状态
    cursor.execute("UPDATE trade SET status=%s WHERE trade_id=%s", (action, trade_id))

    # 如果操作是接收或拒绝交易，更新客户余额
    if action in [1, 2]:
        amount = trade[1]
        cursor.execute("SELECT balance FROM customer WHERE cust_id=%s", (cust_id,))
        balance = cursor.fetchone()[0]
        if action == 1:  # 接收交易
            new_balance = balance + amount
        else:  # 拒绝交易
            new_balance = balance - amount
        cursor.execute("UPDATE customer SET balance=%s WHERE cust_id=%s", (new_balance, cust_id))

    # 创建change记录
    change_id = generate_id()  
    change_time = datetime.now()
    cursor.execute(
        "INSERT INTO change (change_id, change_time, trade_id, cust_id, action) VALUES (%s, %s, %s, %s, %s)",
        (change_id, change_time, trade_id, cust_id, action)
    )

    conn.commit()

    return "交易修改成功"


def verify_phone_and_code(phone, code):
    """
    验证函数：给定手机号、验证码，返回验证码是否正确；（由于不可能真正发送短信，所以使用手机号前4位作为验证码。）

    参数：
    - phone：手机号
    - code：验证码

    返回：
    - 验证结果：True/False
    """
    # 提取手机号的前4位作为验证码
    expected_code = phone[:4]

    # 检查给定的验证码是否正确
    if code == expected_code:
        return True
    else:
        return False
    

 
def get_customer_transactions(cust_id):
    """
    客户交易查询函数：给定客户账号，返回有关客户的所有交易（所有状态）。

    参数：
    - cust_id：客户账号

    返回：
    - 交易：(trade_id, amount, status, cust_a, cust_b)
    """
    conn = mysql.connector.connect(
        host='localhost',  # 数据库主机地址
        user='your_username',  # 数据库用户名
        passwd='your_password',  # 数据库密码
        database='your_database'  # 数据库名
    )
    cursor = conn.cursor()

    # 查询发起的交易
    cursor.execute("SELECT * FROM trade WHERE cust_a=%s", (cust_id,))
    transactions_initiated = cursor.fetchall()

    # 查询接收的交易
    cursor.execute("SELECT * FROM trade WHERE cust_b=%s", (cust_id,))
    transactions_received = cursor.fetchall()

    return transactions_initiated, transactions_received


def get_transactions(date):
    """
    流水查询函数：返回指定日期的流水

    参数：
    - date:日期

    返回：
    - 交易:(trade_id, amount, status, cust_a, cust_b)
    """
    conn = mysql.connector.connect(
        host='localhost',  # 数据库主机地址
        user='your_username',  # 数据库用户名
        passwd='your_password',  # 数据库密码
        database='your_database'  # 数据库名
    )
    cursor = conn.cursor()

    # 计算给定日期的下一天
    next_day = date + timedelta(days=1)

    # 查询给定日期的所有交易
    cursor.execute("SELECT * FROM trade WHERE date >= %s AND date < %s", (date, next_day))
    transactions = cursor.fetchall()

    return transactions


def create_account(name, phone_num, password):
    """
    开户函数：给定姓名、手机号、密码，创建一个客户（创建账户，余额为0，默认限额）

    参数：
    - name：姓名
    - phone_num：手机号
    - password：密码

    返回：
    - 账号ID：新创建的账号ID
    """
    conn = mysql.connector.connect(
        host='localhost',  # 数据库主机地址
        user='your_username',  # 数据库用户名
        passwd='your_password',  # 数据库密码
        database='your_database'  # 数据库名
    )
    cursor = conn.cursor()

    # 生成随机的账号ID和客户ID
    account_id = generate_id()
    cust_id = generate_id()

    # 创建新的账户
    cursor.execute(
        "INSERT INTO account (account_id, password, phone_num) VALUES (%s, %s, %s)",
        (account_id, password, phone_num)
    )

    # 创建新的客户，余额为0，限额为默认值
    default_limit = 10000  # 默认限额
    cursor.execute(
        "INSERT INTO customer (cust_id, name, balance, limit) VALUES (%s, %s, %s, %s)",
        (cust_id, name, 0, default_limit)
    )

    conn.commit()

    return account_id, cust_id

def generate_id():
    """
    返回：
    - 随机生成的5位数
    """
    return random.randint(0, 100000)