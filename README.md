# Mock JSON micro-services

Declare mock endpoints in a single JSON file, then run the server with a tiny alpine docker image.

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

This file is an array of mock requests and responses that the service can handle. Each element of the array is an object with the following keys:

* `method` - required - array of string - request http methods to match against
* `path` - required - string - request url path of the endpoint
* `headers` - optional - object - request headers to match against
* `body` - optional - object - request body JSON to match against
* `response` - required - object
  * `status` - optional (defaults to 200) - string - the status of the response
  * `body` - optional - string or object - the text or JSON of the response

Any requests that are made to the server that are not found in `endpoints.json` respond with a 500 status.

### Running the docker image

Run the docker image `mockservices/mock_json_service` with your `endpoints.json` file mounted to `/config/endpoints.json` inside the container.

```sh
docker run -p 5000:5000 -v $(pwd)/test/mock_service:/config mockservices/mock_json_service
```

Where `$(pwd)/test/mock_service/endpoints.json` is your configuration file.

The above runs a simple python server **exposed on port 5000** that validates your configuration and accepts (or denies) requests according to your mocked endpoints.

I like to keep a `docker-compose.yaml` for testing services using multiple images. Here is an example where we define a mock service alongside other ones:

```yaml
version: '3'

# This docker-compose is for testing

services:

  # For running the app server
  web:
    build: . 
    ...

  # A mock auth server (see test/mock_auth/endpoints.json)
  auth:
    image: mockservices/mock_json_service
    ports:
      - 5000:5000
    volumes:
      - ${PWD}/test/mock_auth:/config
```
