from flask import Flask, render_template
import os
from datetime import datetime

app = Flask(__name__, template_folder='src/templates', static_folder='src/static')
app.config['SECRET_KEY'] = 'raspi-monitor-static'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return {
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'server': 'Raspberry Pi Static Server'
    }

@app.route('/test')
def test():
    return '<h1>Test Endpoint OK</h1><p>Server is responding normally.</p>'

if __name__ == '__main__':
    print("Starting Raspberry Pi Static Monitor on port 5001")
    app.run(host='0.0.0.0', port=5001, debug=False)