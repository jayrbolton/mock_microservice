import os
import sys
import json
import jsonschema
import traceback
import flask
from jsonschema.exceptions import ValidationError

# Load the endpoints data, the schema, and validate the structure

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
    sys.stderr.write('JSON Schema validation Error on endpoints.json:\n')
    sys.stderr.write(str(err) + '\n')
    sys.exit(1)

sys.stdout.write('Loaded %s mock endpoints\n' % len(endpoints))

# Start the Flask app
app = flask.Flask(__name__)
methods = ['GET', 'POST', 'PUT', 'DELETE']


@app.route('/', defaults={'path': ''}, methods=methods)
@app.route('/<path:path>', methods=methods)
def handle_request(path):
    """
    Catch-all: handle any request against the endpoints.json data.
    """
    path = '/' + path
    req_body = json.loads(flask.request.get_data() or '{}')
    method = flask.request.method
    # Find the first endpoint that matches path, method, headers, and body
    for endpoint in endpoints:
        method_ok = method in endpoint.get('methods', ['GET'])
        path_ok = endpoint['path'] == path
        ep_body = endpoint.get('body')
        body_ok = ep_body is None or ep_body == req_body
        headers_ok = match_headers(endpoint)
        if method_ok and path_ok and body_ok and headers_ok:
            sys.stdout.write('Matched endpoint %s %s\n' % (method, path))
            resp = endpoint['response']
            resp_body = flask.jsonify(resp.get('body', ''))
            return (resp_body, resp['status'])
    raise Exception('Unable to match endpoint: %s %s' % (method, path))


@app.errorhandler(Exception)
def any_exception(err):
    """Catch any error with a JSON response."""
    class_name = err.__class__.__name__
    print(traceback.format_exc())
    resp = {'error': str(err), 'class': class_name}
    return (flask.jsonify(resp), 500)


def match_headers(endpoint):
    """
    Either check that there are no headers to match, or match that all headers
    in the endpoint are present and equal in the request.
    """
    if 'headers' not in endpoint:
        return True
    headers = dict(flask.request.headers)
    for (key, val) in endpoint['headers'].items():
        if val != headers.get(key):
            return False
    return True
