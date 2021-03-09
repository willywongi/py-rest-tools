# Python REST tools
A collection of tools to help interacting with JSON REST APIs.
## Rationale
I was writing a lot of code to speak to different API, and while most of them used common interfaces (REST verbs, JSON data...)
almost every API had different ways to handle authentication and pagination. Since I ended up writing a "common ground" method
to access these APIs, I made it into a package.

In this package you'll find a common function that just mounts various parts into the actual request (using, not surprisingly, [requests](https://pypi.org/project/requests/)), and some other basic api client for the services I came across.

## Common client
Provides basic support with building 
```python
# common
from rest_tools.common import common_client

result = common_client(method="get",
                        base_url="https://example.com",
                        path="/api/v1/things",
                        parameters={'page': 1, 'per_page': 10})

# wordpress
from rest_tools.wordpress import get_wordpress_client

wp_client = get_wordpress_client(base_url="https://wp.example.com", 
                                    api_key="api_key", 
                                    api_secret="api_secret")
```
