from flask import Flask
from flask import request, Request
import requests

app = Flask(__name__)


@app.route('/', methods=['GET'])
@app.route('/<path:tmp>', methods=['GET'])
def hello_world(tmp=None):
    if tmp is None:
        tmp = ''
    tmp_request = requests.get('https://rooman-4435f.firebaseio.com/' + tmp)
    return tmp_request.text


@app.route('/', methods=['PATCH'])
@app.route('/<path:tmp>', methods=['PATCH'])
def post_world(tmp=None):
    if tmp is None:
        tmp = ''
    tmp_request = requests.patch('https://rooman-4435f.firebaseio.com/' + tmp, data=request.data)
    return tmp_request.text


if __name__ == '__main__':
    app.run(debug=True, port=8080)
