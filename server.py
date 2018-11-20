import os
import sys
import json
import jsonschema
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
