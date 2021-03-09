""" This module is based on the authentication provided by [JWT Auth](https://github.com/WP-API/jwt-auth).
"""

from operator import itemgetter

import requests

from .common import common_client, expiring


@expiring(itemgetter('exp'))
def get_wordpress_access_token(base_url, api_key, api_secret):
    r = requests.post(f"{base_url}/wp/v2/token", data={'api_key': api_key, 'api_secret': api_secret})
    r.raise_for_status()
    token = r.json()
    return token


def get_wordpress_client(base_url, api_key, api_secret):
    def wordpress_client(method, path="/", parameters=None, url=None, data=None, file_object=None, resource=None):
        token = get_wordpress_access_token(base_url, api_key, api_secret)
        headers = {'Authorization': "Bearer {access_token}".format(access_token=token['access_token'])}
        if method.lower() == 'get' and resource:
            has_more_items = True
            current_page = 1
            resources = []
            while has_more_items:
                paged_parameters = dict(parameters) if parameters else {}
                if current_page != 1:
                    paged_parameters['page'] = current_page

                result = common_client("get", base_url, path=path, parameters=paged_parameters, headers=headers)
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
