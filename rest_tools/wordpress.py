""" This module is based on the authentication provided by [JWT Auth](https://github.com/WP-API/jwt-auth).
"""

from operator import itemgetter
from typing import Callable

import requests

from .common import common_client, expiring, GET, logger


@expiring(itemgetter('exp'))
def get_wordpress_access_token(base_url, api_key, api_secret):
    r = requests.post(f"{base_url}/wp/v2/token", data={'api_key': api_key, 'api_secret': api_secret})
    try:
        r.raise_for_status()
    except requests.HTTPError as exc:
        logger.error("WP Error (%s): %s", exc, r.text)
        raise
    token = r.json()
    return token


def get_wordpress_client(api_key:str, api_secret:str, base_url:str) -> Callable:
    """Returns a callable you can use to interact with Wordpress API.
    :param api_key: Key pair, key
    :param api_secret: Key pair, secret. See https://github.com/WP-API/jwt-auth#generate-key-pairs    
    :param base_url: The installation path of your WP installation; please include `/wp-json` at the end.
    """

    def wordpress_client(method, path="/", parameters=None, url=None, data=None, file_object=None, resource=None):
        """REST tool to interact with Wordpress API.

        :param method: one of the HTTP verb (GET, POST, DELETE,...)
        :param path: the path of the resource (eg.: `/wp/v2/post`)
        :param parameters: the optional query parameters that will be encoded in the querystring.
        :param url: if specified, path and parameters will be ignored (this should be a full URL, eg. `https://www.example.com/wp-json/wp/v2/post`)
        :param data: the optional body content of a POST/PATCH/PUT request. It will be encoded as JSON.
        :param file_object: an open file-like object that will be uploaded.
        :param resource: if this is a string & method is GET, the client will request all the paginated content (it will make 1+ requests as needed). 
        """
        token = get_wordpress_access_token(base_url, api_key, api_secret)
        headers = {'Authorization': "Bearer {access_token}".format(access_token=token['access_token'])}
        if method.lower() == GET and resource:
            has_more_items = True
            current_page = 1
            resources = []
            while has_more_items:
                paged_parameters = dict(parameters) if parameters else {}
                if current_page != 1:
                    paged_parameters['page'] = current_page

                result = common_client(GET, base_url, path=path, parameters=paged_parameters, headers=headers)
                try:
                    total_pages = result['total_pages']
                except KeyError:
                    total_pages = 1

                current_page += 1
                has_more_items = total_pages > current_page
                resources.extend(result[resource])
            return resources

        elif file_object:
            return common_client(method, base_url, path=path, parameters=parameters, url=url, 
                                    headers=headers, form_data=data, files={'file': file_object})
        else:
            return common_client(method, base_url, path=path, parameters=parameters, data=data, url=url, 
                                    headers=headers)

    return wordpress_client
