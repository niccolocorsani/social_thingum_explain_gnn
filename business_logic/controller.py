from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/api/v1/hello')
def api_hello_v1():
    return 'Hello, World! - API v1'

@app.route('/api/v2/hello')
def api_hello_v2():
    return 'Hello, World! - API v2'

if __name__ == '__main__':
    app.run()
