# Mock micro-services

Declare mock endpoints in a single JSON configuration, then run the server in a tiny alpine docker image.

## Quick start

### Writing the endpoints.json file

First, write JSON configuration files that define some endpoints and canned responses.

The following example defines two mock responses for an authentication service -- one for an invalid user, and one for a valid user.

`authorized_whoami.json`

```json
{
  "methods": ["GET"],
  "path": "/whoami",
  "headers": {"Authorization": "Bearer valid_user_token"},
  "response": {
    "status": "200",
    "body": "valid_user_name"
  }
}
```

`unauthorized_whoami.json`

```json
{
  "methods": ["GET"],
  "path": "/whoami",
  "headers": {"Authorization": "Bearer invalid_user"},
  "response": {
    "status": "403",
    "body": "Unauthorized"
  }
}
```

Each mock config file has the following properties:

* `method` - required - array of string - request http methods to match against
* `path` - required - string - request url path of the endpoint
* `headers` - optional - object - request headers to match against
* `body` - optional - string | object - request body to match against
* `response` - required - object
  * `status` - optional (defaults to 200) - string - the status of the response
  * `body` - optional - string or object - the response content
  * `headers` - optional - object - response headers

Any requests that are made to the server that do not match any config file respond with a 500 status.

Check the server logs to debug requests that don't match any endpoints you have defined in your configs.

### Running the docker image

Run the docker image `mockservices/mock_json_service` with your config file directory mounted to `/config` inside the container.

```sh
docker run -p 5000:5000 -v $(pwd)/test/mock_service:/config mockservices/mock_json_service
```

Where `$(pwd)/test/mock_service` contains your json configuration files.

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
