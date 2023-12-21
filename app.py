from flask import Flask, render_template, request
import test  # 导入你的test.py模块

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')  # 返回index.html页面

@app.route('/run_script', methods=['POST'])
def run_script():
    result = test.test()  # 运行test.py中的test函数
    return str(result)  # 返回结果

if __name__ == '__main__':
    app.run(debug=True)
