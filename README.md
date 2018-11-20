# Mock JSON micro-services

> Work in progress; not ready yet

Run a micro JSON server with docker that receives and responds to canned JSON requests with certain parameters.

Declare your mock endpoints in a single JSON file, then run the server with a tiny alpine docker image.

## Quick start

### Writing the endpoints.json file

First, write a JSON configuration file that defines some endpoints and canned responses. Name it `endpoints.json`.

The following example defines two mock responses for an authentication service -- one for an invalid user, and one for a valid user.

```json
[
  {
    "methods": ["GET"],
    "path": "/whoami",
    "headers": {"Authorization": "Bearer valid_user_token"},
    "response": {
      "status": "200",
      "body": "valid_user_name"
    }
  },
  {
    "methods": ["GET"],
    "path": "/whoami",
    "headers": {"Authorization": "Bearer invalid_user"},
    "response": {
      "status": "403",
      "body": "Unauthorized"
    }
  }
]
```

This file is always an array of mock endpoints that the service can respond to. Each element of the array is an object with the following keys:

* `method` - required - array of string - http methods that the endpoint accepts
* `path` - required - string - url path of the endpoint
* `headers` - optional - object - headers that the endpoint accepts
* `response` - required - object
  * `status` - optional (defaults to 200) - string - the status of the response
  * `body` - optional - string or object - the text or JSON of the response

Any requests that are made to the server that are not found in `endpoints.json` respond with a 500 status.

### Running the docker image

Run the docker image `mockeservices/json_service` from docker hub with your `endpoints.json` file mounted to `/config/endpoints.json` in the container.

For example, you might have a `docker-compose.yaml` for running tests, with one service that actually runs your API, and other services that are mocked out using the `mockservices/json_service` image:

```
version: '3'

# This docker-compose file is for testing our server

services:

  # This is the actual server we are testing
  web:
    build: .
    ...

  # This is a mocked secondary service
  auth_service:
    image: mockservices/json_service
    ports:
      - 5000:5000
    # Mount the directory of your endpoints.json file to /config in the container
    # This way, the container has access to /config/endpoints.json
    volumes:
      - test/auth_service:/config
```
