from typing import Callable

import requests

from .common import common_client, GET, logger

def get_pipedrive_client(api_token:str, domain:str) -> Callable:
    """Returns a callable you can use to interact with your instance of Pipedrive.
    You'll need your [personal API token](https://pipedrive.readme.io/docs/how-to-find-the-api-token)
     and the [company domain](https://pipedrive.readme.io/docs/how-to-get-the-company-domain).
    :param api_token: your personal API token
    :param domain: your company domain
    """
    base_url = f"https://{domain}.pipedrive.com/api/v1"
    def pipedrive_client(method, path="/", parameters=None, url=None, data=None, resource=None):
        """REST tool to interact with Wordpress API.

        :param method: one of the HTTP verb (GET, POST, DELETE,...)
        :param path: the path of the resource (eg.: `/deals`)
        :param parameters: the optional query parameters that will be encoded in the querystring.
        :param url: if specified, path and parameters will be ignored (this should be a full URL, eg. `https://www.example.com/wp-json/wp/v2/post`)
        :param data: the optional body content of a POST/PATCH/PUT request. It will be encoded as JSON.
        :param file_object: an open file-like object that will be uploaded.
        :param resource: if this is a string & method is GET, the client will request all the paginated content (it will make 1+ requests as needed).
        """

        _params = {**(parameters or {}), 'api_token': api_token}
        headers = {'Content-Type': 'application/json'}
        if method.lower() == GET and resource:
            # Reference for pagination:
            # https://pipedrive.readme.io/docs/core-api-concepts-pagination
            has_more_items = True
            requested_start = 0
            resources = []
            while has_more_items:
                paged_parameters = dict(_params) if _params else {}
                if requested_start != 0:
                    paged_parameters['start'] = requested_start

                result = common_client(GET, base_url, path=path,
                                       parameters=paged_parameters, headers=headers)
                try:
                    has_more_items = result['additional_data']['pagination']['more_items_in_collection']
                except KeyError:
                    hs_more_items = False

                current_resources = result['data']
                requested_start += len(current_resources)
                resources.extend(current_resources)
            return resources
        else:
            return common_client(method, base_url,
                                 path=path, parameters=parameters, data=data, url=url, headers=headers)

    return pipedrive_client
