#!/usr/bin/env python3
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Test Server Working!</h1><p>If you see this, the server is accessible.</p>'

@app.route('/test')
def test():
    return 'Test endpoint OK'

if __name__ == '__main__':
    print("Starting test server on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)