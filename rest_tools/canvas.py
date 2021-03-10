"""Canvas API Tools.

API reference: https://canvas.instructure.com/doc/api/index.html
"""
import json
from re import compile
from typing import Callable

from .common import get_complete_url, get_response, common_client


def get_canvas_client(access_token:str, base_url:str) -> Callable:
    """Returns a callable you can use to interact with Canvas API. 
    
    :param base_url: Your Canvas canonical URL (e.g. https://your-institution.instructure.com)
    :param access_token: A personal access_token from your user profile page 
        (see: https://canvas.instructure.com/doc/api/file.oauth.html#manual-token-generation)
    """
    headers = {'Authorization': f'Bearer {access_token}'}
    rx = compile(r"<(.*?)>; rel=\"(\w+)\"")

    def canvas_client(method, path="/", parameters=None, url=None, data=None, resource=False):
        """REST tool to interact with Canvas API.

        The path parameters should always start with a "/" and should include the version (eg: `/api/v1/accounts`)
        :param method: one of the HTTP verb (GET, POST, DELETE,...)
        :param path: the path of the resource (eg.: `/api/v1/accounts`)
        :param parameters: the optional query parameters that will be encoded in the querystring.
        :param url: if specified, path and parameters will be ignored (this should be a full URL, eg. `https://example.instructure.com/api/v1/accounts`)
        :param data: the optional body content of a POST/PATCH/PUT request. It will be form-encoded.
        :param resource: if true & method is GET, the client will request all the paginated content (it will make 1+ requests as needed). 
        """
        if method.lower() == "get" and resource:
            resources = []
            next_url = get_complete_url(base_url, path, parameters=parameters, url=url)
            while next_url:
                response = get_response(method, next_url, headers=headers, data=data)
                link_header = response.headers.get('link', '')
                links = {rel: url for url, rel in rx.findall(link_header)}
                contents = response.text
                if contents:
                    resources.extend(json.loads(contents))
                next_url = links.get('next')

            return resources
                
        return common_client(method, base_url, path=path, parameters=parameters, url=url, 
                                headers=headers, form_data=data)
    return canvas_client
