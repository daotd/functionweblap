from flask import Flask 
from flask import abort, jsonify, render_template, request
import pandas as pd

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        df = pd.read_excel(file)
        head = request.form.get('head');
        print(f'selected "{head}"')
    return render_template('index.html')

@app.route('/headers', methods=['POST'])
def headers():
    if 'file' in request.files:
        file = request.files['file']
        df = pd.read_excel(file)
        headers = list(df.columns)
        return jsonify(headers=headers)
    abort(400)