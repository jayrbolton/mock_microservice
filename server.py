import os
import sys
import json
import jsonschema
import traceback
import flask
from jsonschema.exceptions import ValidationError

# Load the endpoints data, the schema, and validate the structure

# For validating every config file
with open('endpoint_schema.json') as fd:
    endpoint_schema = json.load(fd)

if not os.path.exists('/config'):
    sys.stderr.write('Path not found: /config\n')
    sys.exit(1)

endpoints = []
for path in os.listdir('/config'):
    if path.endswith('.json'):
        full_path = '/config/' + path
        with open(full_path) as fd:
            try:
                endpoint = json.load(fd)
            except ValueError as err:
                sys.stderr.write(f'JSON parsing error:\n{err}')
                sys.exit(1)
            try:
                jsonschema.validate(endpoint, endpoint_schema)
            except ValidationError as err:
                sys.stderr.write(f'JSON Schema validation Error for {path}:\n')
                sys.stderr.write(str(err) + '\n')
                sys.exit(1)
            endpoints.append(endpoint)

print(f'Loaded {len(endpoints)} mock endpoints')

# Start the Flask app
app = flask.Flask(__name__)
methods = ['GET', 'POST', 'PUT', 'DELETE']


@app.route('/', defaults={'path': ''}, methods=methods)
@app.route('/<path:path>', methods=methods)
def handle_request(path):
    """
    Catch-all: handle any request against the endpoints.json data.
    """
    print('-' * 80)
    path = '/' + path
    req_body = flask.request.get_data().decode() or ''
    method = flask.request.method
    # Find the first endpoint that matches path, method, headers, and body
    for endpoint in endpoints:
        if endpoint['path'] == path:
            print('Matched path:', path)
        else:
            continue
        expected_methods = endpoint.get('methods', ['GET'])
        if method in expected_methods:
            print('Matched method')
        else:
            msg = f'Mismatch on method: {method} vs {expected_methods}'
            print(msg)
            continue
        if match_headers(endpoint):
            print('Matched headers')
        else:
            hs = dict(flask.request.headers)
            expected_hs = endpoint.get('headers')
            msg = f'Mismatch on headers:\n  got:      {hs}\n  expected: {expected_hs}'
            print(msg)
            continue
        expected_body = endpoint.get('body', '')
        if isinstance(expected_body, dict):
            expected_body_json = json.dumps(expected_body)
            try:
                given_body_json = json.dumps(json.loads(req_body))
            except Exception as err:
                print('Error parsing json body:', str(err))
                continue
            body_ok = expected_body_json == given_body_json
        else:
            body_ok = expected_body.strip() == req_body.strip()
        if body_ok:
            print('Matched body')
        else:
            msg = f'Mismatch on body:\n  got:      {req_body}\n  expected: {expected_body}'
            print(msg)
            continue
        print('Matched endpoint {} {}'.format(method, path))
        return mock_response(endpoint.get('response', {}))
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


def mock_response(config):
    """
    Create a mock flask response from the endpoints.json configuration
    """
    resp_body = config.get('body')
    if isinstance(resp_body, dict):
        resp_body = json.dumps(resp_body)
    resp = flask.Response(resp_body)
    resp.status = config.get('status', '200')
    for (header, val) in config.get('headers', {}).items():
        resp.headers[header] = val
    return resp
