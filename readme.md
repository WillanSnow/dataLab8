# 选题

## 电子钱包

主要实现功能：
- 客户之间进行交易、查看交易详情、统计查看等等
  - 身份验证、统计交易
- 管理员查看交易记录
- 登录验证。。

客户：存钱、取钱、交易（收、发）、查看账户的交易记录、<申请注销>、用户限额

经理：管理客户（开户、修改密码、注销、提升限额），查看记录，查看月流水

通用：登录验证（账号、密码、手机号）。

# 分工

1. 文档+主程序：主程序（gui、调用接口），写文档；
2. 接口部分+ppt：程序访问数据库的函数、展示ppt、部分数据库实现；
3. 数据库部分：部分数据库实现

数据库实现包含：数据库设计；表、用户、权限、触发器，初始化一些数据等等。

分工可以再调整，感觉数据库部分可能会多一点，最后每个人可能都会写一点文档、ppt。

前端：实现展示框架、调用接口(陈瑞祺)
后端：数据库设计、*(实现、接口实现)*
报告：文档、ppt

# 数据库设计

以功能为导向：

**实体集：**

1. **账户**：账号，密码，手机号
2. **客户**：客户ID，姓名，余额，限额（单日、单笔）
3. **经理**：经理ID，姓名
4. **交易**：交易ID，发起客户，接收客户，交易状态，金额

**关系集：**

- 账户-客户：拥有
- 账户-经理：拥有
- 客户-交易：修改交易状态（发起、接收、拒绝、撤销）、修改时间
- 经理-交易：强制回退交易、修改时间、
- 经理-客户：开户、销户、修改密码、修改限额
- 经理不能修改自己的密码，只能通过后台的数据库管理员。

**约束**：
- 账户：
  - 账号为主键
  - 密码不能为空。
- 客户：
  - 客户id为主键
- 经理：
  - 经理id为主键
- 交易：
  - 交易id为主键

# 开发日志

新建数据库，用于本次实验：

![](imgs/2023-12-20-20-11-20.png)

使用pymysql库实现python访问数据库。


当然，以下是使用Flask的一些基本步骤：

1. **安装Flask**：你可以使用pip来安装Flask。在命令行中输入以下命令：

```bash
pip install flask
```

2. **创建一个Flask应用**：首先，你需要导入Flask模块并创建一个应用实例。Flask使用Python的模块和包来组织代码。

```python
from flask import Flask
app = Flask(__name__)
```

3. **定义路由和视图函数**：Flask使用路由来决定当用户访问一个特定的URL时，应该运行哪个Python函数（也被称为视图函数）。

```python
@app.route('/')
def home():
    return "Hello, World!"
```

在这个例子中，我们定义了一个视图函数`home`，它返回字符串"Hello, World!"。我们使用`app.route`装饰器来告诉Flask，当用户访问根URL（'/'）时，应该调用这个函数。

4. **运行应用**：最后，我们需要告诉Flask开始运行我们的应用。

```python
if __name__ == '__main__':
    app.run(debug=True)
```

5. **在HTML中使用Python函数的结果**：你可以使用`render_template`函数来渲染一个HTML模板，并将Python函数的结果传递给模板。例如，假设你有一个名为`index.html`的模板，你可以这样做：

```python
from flask import render_template

@app.route('/')
def home():
    message = "Hello, World!"
    return render_template('index.html', message=message)
```

然后，在`index.html`模板中，你可以使用`{{ message }}`来显示这个消息。

```html
<!doctype html>
<html>
    <body>
        <h1>{{ message }}</h1>
    </body>
</html>
```

这只是Flask的基础使用方法。Flask还有许多其他的功能，比如处理表单数据、文件上传、用户认证等等。你可以查阅[Flask的官方文档](http://flask.pocoo.org/docs/)来了解更多信息。希望这个信息能帮助你！如果你有任何其他问题，欢迎随时向我提问。😊