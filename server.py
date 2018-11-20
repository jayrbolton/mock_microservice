import os
import sys
import json
import jsonschema
import flask
from jsonschema.exceptions import ValidationError

with open('endpoints_schema.json') as fd:
    endpoints_schema = json.load(fd)


if not os.path.exists('/config/endpoints.json'):
    sys.stderr.write('File not found: /config/endpoints.json\n')
    sys.exit(1)

with open('/config/endpoints.json') as fd:
    endpoints = json.load(fd)
try:
    jsonschema.validate(endpoints, endpoints_schema)
except ValidationError as err:
    sys.stderr.write('Validation Error on endpoints.json:\n')
    sys.stderr.write(str(err) + '\n')
    sys.exit(1)

sys.stdout.write('Loaded %s mock endpoints\n' % len(endpoints))

app = flask.Flask(__name__)
methods = ['GET', 'POST', 'PUT', 'DELETE']


@app.route('/', defaults={'path': ''}, methods=methods)
@app.route('/<path:path>', methods=methods)
def handle_request(path):
    path = '/' + path
    req_body = flask.request.get_data()
    try:
        req_json = json.loads(req_body)
    except Exception:
        req_json = None
    method = flask.request.method
    print(req_json)
    print(req_body)
    print(endpoints)
    found_endpoint = None
    for endpoint in endpoints:
        if method not in endpoint['methods']:
            continue
        if endpoint['path'] != path:
            continue
        if 'headers' not in endpoint:
            found_endpoint = endpoint
            break
        headers = dict(flask.request.headers)
        headers_match = True
        for (key, val) in endpoint['headers'].items():
            if key not in headers or val != headers[key]:
                headers_match = False
                break
        if headers_match:
            found_endpoint = endpoint
    if found_endpoint:
        return (
            found_endpoint['response']['body'],
            found_endpoint['response']['status']
        )
    else:
        return ('"Unknown endpoint."', 500)
