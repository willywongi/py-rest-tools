"""Directus API tools.

Documentation and reference: https://docs.directus.io/reference/introduction/
"""
import json

from .common import common_client, GET

def get_directus_client(token, base_url):
    """Returns a callable you can use to interact with your Directus instance API
    :param token: A _static token_ for the user
        (see: https://docs.directus.io/reference/authentication/#access-tokens)
    :param base_url: the complete base URL of your directus instance (eg.: https://directus.example.com)
        (no trailing slash)
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    def directus_client(method, path, parameters=None, url=None, data=None, resource=False):
        _parameters = {**parameters} if parameters else {}
        current_filter = _parameters.pop('filter', None)
        if current_filter:
            _parameters['filter'] = json.dumps(current_filter)
        
        if method.lower() == GET and resource:
            has_more_items = True
            results = []
            while has_more_items:
                params = {**_parameters} if parameters else {}
                if len(results):
                    params['offset'] = len(results)
                # Returns the item count of the collection you're querying, 
                # taking the current filter/search parameters into account.
                # https://docs.directus.io/reference/query/#filter-count
                params['meta'] = 'filter_count'

                result = common_client(GET, base_url, path=path, parameters=params, 
                                        headers=headers)
                filter_count = result['meta']['filter_count']
                results.extend(result['data'])
                has_more_items = len(results) > filter_count

        else:
            response = common_client(method, base_url, path, parameters, url, headers, data)
            if response:
                results = response['data']
            else:
                results = response

        return results

    return directus_client
