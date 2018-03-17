from flask import Flask
from flask import request, Response
from models.controllers import RelayManager
import requests
import json

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = RelayManager('root', 'password', 'localhost', port=3306)
app.config['SQLALCHEMY_DATABASE_URI'] = db.uri
db.create_db()
db.connect_to_db()
db.create_tables()
db.db.init_app(app)


@app.route('/<url_id>/<path:tail>')
def manage_relay(url_id, tail=None):
    if tail is None:
        tail = ''

    url_head = db.get_url_head(url_id)
    print(request.method)
    return_data = None
    if request.method == 'GET':
        return_data = requests.get(url_head + '/' + tail)
    elif request.method == 'PUT':
        return_data = requests.put(url_head + '/' + tail, data=request.data)
    elif request.method == 'PATCH':
        return_data = requests.put(url_head + '/' + tail, data=request.data)
    elif request.method == 'POST':
        return_data = requests.post(url_head + '/' + tail, data=request.data)
    else:
        return return_error(400, 'The method "%s" is not supported yet' % request.method)

    return convert_response(return_data)

@app.route('/api/add_relay', methods=['POST'])
def add_relay():
    try:
        json_data = request.json
        dest_url = json_data['url']
        secret_key = json_data['key']
        return_data = {'key': db.add_relay(secret_key, dest_url)}
        if return_data is None:
            return return_error(500, 'Something went wrong')
        return return_formatted_data(200, return_data)
    except Exception as e:
        return return_error(400, e)


def return_error(status_code, error):
    error_json = {'error': {'message': str(error)}}
    return Response(status=status_code, response=json.dumps(error_json))


def return_formatted_data(status_code, data):
    msg_json = {'data': data}
    return Response(status=status_code, response=json.dumps(msg_json))

def convert_response(https_response):
    return Response(status=https_response.status_code, headers=https_response.headers.items(), response=https_response.content)



if __name__ == '__main__':
    app.run(debug=True, port=8080)
