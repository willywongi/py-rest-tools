# Python REST tools
A collection of tools to help interacting with JSON REST APIs.
## Rationale
I was writing a lot of code to speak to different API, and while most of them used common interfaces (REST verbs, JSON data...)
almost every API had different ways to handle authentication and pagination. Since I ended up writing a "common ground" method
to access these APIs, I made it into a package.

In this package you'll find a common function that just mounts various parts into the actual request (using, not surprisingly, [requests](https://pypi.org/project/requests/)), and some other basic api client for the services I came across.

## Common client
Every function uses a common client with basic support for JSON body request/response and query parameters. Things get a bit more useful when you use a pre-baked client for a popular service.
```python
# common
from rest_tools.common import common_client

result = common_client(method="get",
                        base_url="https://example.com",
                        path="/api/v1/things",
                        parameters={'page': 1, 'per_page': 10})

# wordpress
from rest_tools.wordpress import get_wordpress_client

wp_client = get_wordpress_client(base_url="https://wp.example.com/wp-json", 
                                    api_key="api_key", 
                                    api_secret="api_secret")
wp_client("get", "/wp/v2/post", resource="posts")
```
Once you set up the client with the `base_url` and the auth parameters, you'll be able to query the resources in your Wordpress installation. Infact, if you `get` a resource like your blog's posts and include the name of the resource (`resource="posts"`), the client will automatically issue a number of requests to fetch all the resources from the paginated endpoint. 

All of the clients share the same API; minor variations are detailed later on.

### `get_<service>_client(base_url, **auth_details)` 

- `base_url`: if the service is in cloud (SaaS), this info is already configured.
- `**auth_details`: every client does this differently (see details)

### `<service>_client(method, path="/", parameters=None, url=None, data=None, resource=None)`
- `method`: one of the common http verbs: get, post, put, patch, delete...
- `path`: always starts with a `/`.
- `parameters`: this dictionary becomes `?search=foo&exclude=bar`.
- `url`: if specified, path and parameters will be ignored (this should be a full URL, eg. `https://example.com/api/v1/things`).
- `data`: the optional body content of a POST/PATCH/PUT request. It will be encoded as JSON according to the service.
- `resource`: this could be a bool or a string, depending on how the service responds. It is used to pull all the resources from a paginated endpoint.
```python
from rest_tools.example import get_example_client

example_client = get_example_client(base_url="https://www.example.com/api/v1",
                                    api_key="apikey",
                                    api_secret="apisecret")

foo_things = example_client(method="get",
                            path="/things",
                            parameters={'search': 'foo', 'exclude': 'bar'},
                            url=None,
                            data=None,
                            resource="things")
```

## Clients
All these clients are packaged and documented (in code).
### Canvas
#### `get_canvas_client(access_token, base_url)`
- `access_token`: A personal access_token from your user profile page (see: https://canvas.instructure.com/doc/api/file.oauth.html#manual-token-generation)
- `base_url`: Your Canvas canonical URL (e.g. https://your-institution.instructure.com)
### ClickUp
#### `get_clickup_client(api_token, base_url)`
- `api_token`: A personal token from the *Apps* section in your User Settings (see: https://jsapi.apiary.io/apis/clickup20/introduction/authentication/personal-token.html).
- `base_url`: the default should be changed only if asked from ClickUp
### Eventbrite
#### `get_eventbrite_client(token, base_url)`
 - `token`: A token from your developer profile page (see: https://www.eventbrite.com/platform/api#/introduction/authentication).
 - `base_url`: the default should be changed only if asked from Eventbrite
### Fusionauth
#### `get_fusionauth_client(api_key, base_url)`
 - `api_key`: the api key, see: https://fusionauth.io/docs/v1/tech/apis/authentication/#api-key-authentication
 - `base_url`: the url of your Fusionauth instance

### Livestorm
#### `get_livestorm_client(apikey, base_url)`
 - `apikey`: A token from the Account Settings > Integrations page
    (see: https://developers.livestorm.co/docs/authorization)
 - `base_url`: the default should be changed only if asked from Livestorm
### Mailchimp
#### `get_mailchimp_client(access_token, base_url)`
 - `access_token`: A apikey from your developer profile page (see: https://mailchimp.com/developer/marketing/docs/fundamentals/#authenticate-with-an-api-key).
 - `base_url`: the default should be changed only if asked from Mailchimp
### Wordpress
#### `get_wordpress_client(api_key, api_secret, base_url)`
This client requires the [JWT Auth plugin](https://github.com/WP-API/jwt-auth) to [generate key pair](https://github.com/WP-API/jwt-auth#generate-key-pairs).
 - `api_key`: Key pair, key
 - `api_secret`: Key pair, secret. 
 - `base_url`: The installation path of your WP installation; please include `/wp-json` at the end.
### Directus
#### `get_directus_client(token, base_url)`
 - `token`: A _static token_ for the user (see: https://docs.directus.io/reference/authentication/#access-tokens)
 - `base_url`: the complete base URL of your Directus instance (eg.: https://directus.example.com - no trailing slash)
