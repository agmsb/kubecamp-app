from flask import Flask, request, render_template, abort
import os

app = Flask(__name__)
fancy_feature = os.environ.get('ENABLE_FEATURE')

@app.route('/')
def hello():
    return render_template('index.html', fancy_feature=fancy_feature)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)