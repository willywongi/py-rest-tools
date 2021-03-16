"""Livestorm API tools.

API reference: https://developers.livestorm.co/reference
"""
from .common import common_client, GET

def get_livestorm_client(apikey, base_url="https://api.livestorm.co/v1"):
    """Returns a callable you can use to interact with Livestorm API.
    :param apikey: A token from the Account Settings > Integrations page
        (see: https://developers.livestorm.co/docs/authorization)
    :param base_url: the default should be changed only if asked from Livestorm
    """
    headers = {
		"accept": "application/vnd.api+json",
		"Authorization": apikey
	}
    def livestorm_client(method, path, parameters=None, url=None, data=None, resource=False):
        """REST tool to interact with Livestorm API.

        The path parameters should always start with a "/" and should NOT include the version (eg: `/events`)
        :param method: one of the HTTP verb (GET, POST, DELETE,...)
        :param path: the path of the resource (eg.: `/events`)
        :param parameters: the optional query parameters that will be encoded in the querystring.
        :param url: if specified, path and parameters will be ignored (this should be a full URL, eg. `https://api.livestorm.co/v1`)
        :param data: the optional body content of a POST/PATCH/PUT request. It will be encoded as JSON.
        :param resource: if true & method is GET, the client will request all the paginated content (it will make 1+ requests as needed). 
        """
        if method.lower() == GET and resource:
            has_more_items = True
            current_page = 0
            results = []
            while has_more_items:
                paged_parameters = dict(parameters) if parameters else {}
                if current_page != 0:
                    paged_parameters['page[number]'] = current_page

                result = common_client(GET, base_url, path=path, parameters=paged_parameters, 
                                        headers=headers)
                try:
                    page_count = result['meta']['page_count']
                except KeyError:
                    page_count = 1

                current_page += 1
                has_more_items = page_count > current_page
                results.extend(result['data'])

        else:
            response = common_client(method, base_url, path, parameters, url, headers, data)
            if response:
                results = response['data']
            else:
                results = response

        return results
    return livestorm_client
