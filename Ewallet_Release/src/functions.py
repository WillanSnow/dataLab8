## This file contains all the functions used in the project.
## You need to install this library, you can use pip to install pip install mysql-connector-python
## including tables: trade,customer,change_trade,account,manager
## table :
# - account：
#   - 账号：标识码，创建账户时，需要随机生成8位数。account_id（int）
#   - 密码：9字符以内的字符串 password(string)
#   - 手机号：固定长度为11的一串数字 phone_num(string)
# - 客户：
#   - 客户id：5位数字标识码，随机生成或累计的形式。cust_id(int)
#   - 姓名：客户的名字    name(string)
#   - 余额：账户余额，发起交易时，直接扣除；接收交易时，才增加到目标用户；拒绝交易时，金额回到发起客户余额。balance(float)
#   - 限额：单笔交易的限额。limit(float)
# - 交易：
#   - 交易id：9位数字标识码；trade_id(int)
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
from datetime import datetime, timedelta, date

# -----------------数据库函数----------------------

def login(account, password, conn):
    """
    登录函数：给定account、password，返回登录结果（-1：登录失败，账号不存在；0：登录失败，密码错误；1：登录成功）

    参数：
    - account：账号
    - password：密码
    - conn:数据库连接

    返回：
    - 登录结果：-1：登录失败，账号不存在；0：登录失败，密码错误；1：登录成功
    """
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM account WHERE account_id =%s", (account,))
    result = cursor.fetchone()

    if result is None:
        return "账号不存在"         # 账号不存在
    elif result[0] != password:
        return "密码错误"           # 密码错误
    else:
        return "success"                  # 登录成功

def get_pending_transactions(cust_id, conn):
    """
    消息提醒函数：给定account，返回等待其确认的交易(即发给他且他未确认的交易)

    参数：
    - account：账号
    - conn:数据库连接

    返回：
    - 等待确认的交易：(trade_id, amount, status, cust_a, cust_b)
    """
    cursor = conn.cursor()
    ret = {"flag":False, "info":"", "dota":[]}
    
    # 查询交易
    cursor.execute("SELECT trade_id, cust_a, cust_b, amount, status FROM trade WHERE cust_a =%s OR cust_b = %s", (cust_id, cust_id, ))
    result = cursor.fetchall()

    if result == []:
        ret["info"] = "该客户没有交易记录。"
    else:
        status_str = ["待确认", "已完成", "未成功"]
        for row in result:
            row = list(row)
            # 提取名字
            cursor.execute("SELECT name FROM customer WHERE cust_id = %s", (row[1], ))
            row[1] = cursor.fetchone()[0]

            cursor.execute("SELECT name FROM customer WHERE cust_id = %s", (row[2], ))
            row[2] = cursor.fetchone()[0]

            row[4] = status_str[row[4]]
            print(row)
            ret["dota"].append(row)

        ret["flag"] = True
        ret["info"] = "查询客户的交易记录如下。"

    return ret


def initiate_transaction(account_a, account_b, amount, conn):
    """
    交易发起函数：给定发起客户、目标客户、金额，若目标客户不存在，金额超过发起客户单笔额度，交易发起失败，返回失败信息；否则发起成功，创建交易(注意创建交易、change元组)。
    注意：存、取、交易都是通过这个函数实现的，存由‘系统’账户发起，客户接收；取由客户发起，‘系统’接收。

    参数：
    - cust_a：发起客户
    - cust_b：目标客户
    - amount：金额
    - conn:数据库连接

    返回：
    - 交易发起结果：交易发起成功/失败信息
    """
    cursor = conn.cursor()
    cust_b = None
    cust_a = None
    amount = float(amount)

    # 检查目标客户是否存在
    print(account_a, account_b)
    cursor.execute("SELECT cust_id FROM customer WHERE account_id=%s", (account_b, ))
    cust_b = cursor.fetchone()
    if cust_b is None:
        return "目标客户不存在。"
    else:
        cust_b = cust_b[0]

    cursor.execute("SELECT account_id FROM account WHERE account_id = %s", (account_b ,))
    if cursor.fetchone() is None:
        return "目标客户已注销。"

    # 获取发起用户信息
    cursor.execute("SELECT cust_id FROM customer WHERE account_id = %s", (account_a, ))
    cust_a = cursor.fetchone()[0]

    # 检查金额是否超过发起客户的单笔限额
    if account_a == 0:
        cursor.execute("SELECT `limit`, balance FROM customer WHERE cust_id = %s", (cust_b, ))
    else:
        cursor.execute("SELECT `limit`, balance FROM customer WHERE cust_id=%s", (cust_a,))
    limit = cursor.fetchone()

    if amount > limit[0]:
        return "交易金额超过账户的单笔交易限额，请重新设置。"
    elif cust_a != 0 and amount > limit[1]:
        return "余额不足，请重新输入。"

    # 创建交易记录
    trade_id = generate_id(9)
    cursor.execute(
        "INSERT INTO trade (trade_id, amount, status, cust_a, cust_b) VALUES (%s, %s, 0, %s, %s)",
        (trade_id, amount, cust_a, cust_b)
    )

    # 创建change记录
    change_id = generate_id(9)
    change_time = datetime.now()
    cursor.execute(
        "INSERT INTO changes (change_id, change_time, trade_id, cust_id, action) VALUES (%s, %s, %s, %s, 0)",
        (change_id, change_time, trade_id, cust_a, )
    )

    # 交易发起，余额立即减少
    if cust_a != 0:
        cursor.execute("SELECT balance FROM customer WHERE cust_id = %s", (cust_a, ))
        new_balance = cursor.fetchone()[0]
        new_balance -= amount
        cursor.execute("UPDATE customer SET balance=%s WHERE cust_id = %s", (new_balance, cust_a, ))

    conn.commit()

    if cust_a == 0 or cust_b == 0:
        # 如果是存钱/取钱，接收方立即接收
        modify_transaction(cust_b, trade_id, 1, conn)
    return "1"

def modify_transaction(cust_id, trade_id, action, conn):
    """
    修改交易：给定客户、交易、操作(接收、撤销、拒绝)，修改数据库对应信息(注意同步余额、trade状态，增加change条目)

    参数：
    - cust_id：客户
    - trade_id：交易
    - action：操作(接收、撤销、拒绝)
    - conn:数据库连接

    返回：
    - 交易修改结果：交易修改成功/失败信息
    """
    cursor = conn.cursor()

    # 获取交易信息
    cursor.execute("SELECT cust_a, cust_b, amount FROM trade WHERE trade_id=%s", (trade_id,))
    trade = cursor.fetchone()
    if trade is None:
        return "交易不存在"
    else:
        cust_a = trade[0]
        cust_b = trade[1]
        amount = trade[2]

    # 检查操作是否合法
    if action not in [0, 1, 2, 3, 4]:
        return "操作不合法"

    # 更新交易状态
    cursor.execute("UPDATE trade SET status=%s WHERE trade_id=%s", (action, trade_id, ))

    # 如果操作是接收或拒绝交易，更新客户余额
    # if action in [1, 2]:
    if action == 1:
        # 接收交易
        cursor.execute("SELECT balance FROM customer WHERE cust_id=%s", (cust_b,))
        balance = cursor.fetchone()[0]
        new_balance = balance + amount
        cursor.execute("UPDATE customer SET balance=%s WHERE cust_id=%s", (new_balance, cust_b, ))
    elif action == 2:
        # 拒绝交易
        cursor.execute("SELECT balance FROM customer WHERE cust_id=%s", (cust_a,))
        new_balance = balance + amount
        cursor.execute("UPDATE customer SET balance=%s WHERE cust_id=%s", (new_balance, cust_a, ))

    # 创建change记录
    change_id = generate_id(9)
    change_time = datetime.now()
    cursor.execute(
        "INSERT INTO changes (change_id, change_time, trade_id, cust_id, action) VALUES (%s, %s, %s, %s, %s)",
        (change_id, change_time, trade_id, cust_id, action)
    )

    conn.commit()

    return "交易修改成功"

def get_customer_transactions(account, conn):
    """
    客户交易查询函数：给定客户账号，返回有关客户的所有交易（所有状态）。

    参数：
    - cust_id：客户账号
    - conn:数据库连接

    返回：
    - 交易：(trade_id, amount, status, cust_a, cust_b)
    """
    ret = {"flag": False, "info": "", "dota": []}
    if len(account) > 5 or not account.isdigit():
        ret["info"] = "账号格式不合法，请重新输入。"
        return ret
    cursor = conn.cursor()

    # 客户注销后，客户、交易、记录不会删除。
    cursor.execute("SELECT cust_id FROM customer WHERE account_id = %s", (account, ))
    cust_id = cursor.fetchone()

    if cust_id is None:
        ret["info"] = "该账户没有注册过！"
        return ret
    else:
        cust_id = cust_id[0]

    # 查询交易
    cursor.execute("SELECT trade_id, cust_a, cust_b, amount, status FROM trade WHERE cust_a=%s OR cust_b = %s", (cust_id, cust_id, ))
    result = cursor.fetchall()

    if result == []:
        ret["info"] = "该客户没有交易记录。"
    else:
        status_str = ["待确认", "已完成", "未成功"]
        for row in result:
            row = list(row)
            # 提取名字
            cursor.execute("SELECT name FROM customer WHERE cust_id = %s", (row[1], ))
            row[1] = cursor.fetchone()[0]

            cursor.execute("SELECT name FROM customer WHERE cust_id = %s", (row[2], ))
            row[2] = cursor.fetchone()[0]

            row[4] = status_str[row[4]]
            print(row)
            ret["dota"].append(row)

        ret["flag"] = True
        ret["info"] = "查询客户的交易记录如下。"

    return ret

def get_transactions(conn, get_date = date.today()):
    """
    流水查询函数：返回指定日期的流水

    参数：
    - date:日期
    - conn:数据库连接

    返回：
    - 交易:(trade_id, amount, status, cust_a, cust_b)
    """
    cursor = conn.cursor()

    # 计算给定日期的下一天
    next_day = get_date + timedelta(days=1)

    # 从changes表中查询给定日期的所有交易ID
    cursor.execute("SELECT trade_id FROM changes WHERE change_time >= %s AND change_time < %s", (get_date, next_day))
    trade_ids = [row[0] for row in cursor.fetchall()]

    # 从trade表中筛选这些交易
    liusum = 0
    for trade_id in trade_ids:
        cursor.execute("SELECT amount FROM trade WHERE trade_id = %s", (trade_id,))
        liusum += cursor.fetchone()[0]

    return liusum

def create_account(name, phone_num, password, conn):
    """
    开户函数：给定姓名、手机号、密码，创建一个客户（创建账户，余额为0，默认限额）

    参数：
    - name：姓名
    - phone_num：手机号
    - password：密码
    - conn:数据库连接

    返回：
    - 账号ID：新创建的账号ID
    """
    cursor = conn.cursor()

    # 生成随机的账号ID和客户ID
    account_id = generate_id(5)
    cust_id = generate_id(5)

    # 创建新的账户
    cursor.execute(
        "INSERT INTO account (account_id, password, phone_num) VALUES (%s, %s, %s)",
        (account_id, password, phone_num)
    )

    # 创建新的客户，余额为0，限额为默认值
    default_limit = 10000  # 默认限额
    cursor.execute(
        "INSERT INTO customer VALUES (%s, %s, %s, %s, %s)",
        (cust_id, name, 0, default_limit, account_id    )
    )

    conn.commit()

    return account_id, cust_id

def generate_id(n):
    """
    返回：
    - 随机生成的n位数
    """
    return random.randint(0, int(10**n))

def get_account_infomation(account, conn):
    "获取账户的基本信息"
    cursor = conn.cursor()
    cursor.execute("SELECT phone_num, password FROM account WHERE account_id =%s", (account,))
    
    return cursor.fetchone()

def change_psd(account, psd, conn):
    "修改指定账户的密码"
    cursor = conn.cursor()
    cursor.execute("UPDATE account SET password = %s WHERE account_id = %s", (psd, account, ))

    conn.commit()

def get_account_type(account_id, conn):
    "获取账号的用户类型，True = Manager，False = Customer"
    cursor = conn.cursor()
    cursor.execute("SELECT manager_id FROM manager WHERE account_id = %s", (account_id,))
    result = cursor.fetchone()

    if result is None:
        cursor.execute("SELECT cust_id FROM customer WHERE account_id = %s", (account_id,))
        return  False, cursor.fetchone()[0]
    else:
        return True, result[0]

def get_manager_info(account, conn):
    "返回经理的姓名信息"
    cursor = conn.cursor()
    cursor.execute("SELECT name, manager_id FROM manager WHERE account_id = %s", (account,))

    result = cursor.fetchone()
    if result is None:
        return "Data Error"
    else:
        return result
    
def delete_cust(account, conn):
    "注销账户"
    cursor = conn.cursor()
    cursor.execute("SELECT* FROM customer WHERE account_id = %s", (account,))
    is_cust = cursor.fetchone()

    cursor.execute("SELECT * FROM manager WHERE account_id = %s", (account, ))
    is_manager = cursor.fetchone()

    cursor.execute("SELECT * FROM account WHERE account_id = %s", (account, ))
    is_account = cursor.fetchone()
    
    if is_manager is not None:
        return {"flag": False, "info": "无权注销该账户。"}
    elif is_cust is None:
        return {"flag": False, "info":"账户不存在。"}
    elif is_account is None:
        return {"flag": False, "info": "用户已注销。"}
    else:
        cursor.execute("DELETE FROM account WHERE account_id = %s", (account,))

        conn.commit()
        return {"flag" : True, "info":"注销账户成功。"}

def update_limit(account, amount, conn):
    "修改账户限额"
    if len(amount) > 10 or not amount.isdigit():
        return {"flag": False, "info": "额度格式不正确，请重新输入。"}

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customer WHERE account_id = %s", (account, ))
    is_cust = cursor.fetchone()
    if is_cust is None:
        return {"flag": False, "info": "用户不存在。"}
    
    cursor.execute("SELECT * FROM account WHERE account_id = %s", (account, ))
    is_account = cursor.fetchone()

    if is_account is None:
        return {"flag": False, "info": "用户已注销。"}
    else:
        cursor.execute("UPDATE customer SET `limit` = %s WHERE account_id = %s", (amount, account))
        conn.commit()
        return {"flag": True, "info": "修改额度成功。"}

def get_cust_info(account, conn):
    "返回客户的基本信息"
    cursor = conn.cursor()

    cursor.execute("SELECT name, cust_id, balance, `limit` FROM customer WHERE account_id = %s", (account, ))

    result = cursor.fetchone()
    return result

# ---------------服务器的一些函数----------------------

def legal_phone(phone):
    "判断电话号码是否合法"
    if len(phone) != 11 or not phone.isdigit():
        return False
    else:
        return True
    
# 更改记录
# 修改了 grand_id ，使能随机生成 n 位编号，这样的话，数据库使用的自增编号就没什么用了，都用grand_id生成编号：客户、经理、账户的 id 为 5 位；其余为9位。
# 更改数据库 change、trade 的 id 属性为 9 位整数，因为 15 位超 sql int 范围了。
    
# 修改查询指定日期流水函数：默认返回当日流水，且仅记录已完成的交易流水。
    
# 修改：limit数据库中仍存放 float，但取值都是整数，因为前端输入比较好处理。
    
# 修改数据库：修改changes, trade的外键约束等级，使客户注销后，其交易、活动记录依然保留。