import pymysql

def test():
    return 123

# 连接数据库，创建连接对象connection
# 连接对象作用是：连接数据库、发送数据库信息、处理回滚操作（查询中断时，数据库回到最初状态）、创建新的光标对象
connection = pymysql.connect(
    host='localhost',  # 数据库服务器地址
    user='username',  # 用户名
    password='password',  # 密码
    db='database_name'  # 数据库名
)

# 使用cursor()方法获取操作游标
cursor = connection.cursor()

# 编写SQL查询
sql_query = "SELECT * FROM table_name"

# 执行SQL查询
cursor.execute(sql_query)

# 获取所有返回的数据
results = cursor.fetchall()

# 打印数据
for row in results:
    print(row)

# 关闭数据库连接
connection.close()