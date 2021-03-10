"""Eventbrite API tools.

API reference: https://www.eventbrite.com/platform/api
"""
from typing import Callable
from .common import common_client, GET

def get_eventbrite_client(token:str, base_url:str="https://www.eventbriteapi.com/v3") -> Callable:
    """Returns a callable you can use to interact with Eventbrite API.
    :param token: A token from your developer profile page
        (see: https://www.eventbrite.com/platform/api#/introduction/authentication)
    :param base_url: the default should be changed only if asked from Eventbrite
    """
    headers = {
		"Authorization": f"Bearer {token}",
		"Content-Type": "application/json"
	}
    def eventbrite_client(method, path, parameters=None, url=None, data=None, resource=None):
        """REST tool to interact with Eventbrite API.

        The path parameters should always start with a "/" and should NOT include the version (eg: `/events`)
        :param method: one of the HTTP verb (GET, POST, DELETE,...)
        :param path: the path of the resource (eg.: `/events`)
        :param parameters: the optional query parameters that will be encoded in the querystring.
        :param url: if specified, path and parameters will be ignored (this should be a full URL, eg. `https://www.eventbriteapi.com/v3/events`)
        :param data: the optional body content of a POST/PATCH/PUT request. It will be encoded as JSON.
        :param resource: if this is a string & method is GET, the client will request all the paginated content (it will make 1+ requests as needed). 
        """
        if method.lower() == GET and resource:
            has_more_items = True
            continuation = None
            resources = []

            while has_more_items:
                query_args = dict(parameters) if parameters else {}
                if continuation:
                    query_args['continuation'] = continuation

                result = common_client(GET, base_url, path, parameters=query_args, headers=headers)
                has_more_items = result['pagination']['has_more_items']
                if has_more_items:
                    continuation = result['pagination']['continuation']
                resources.extend(result[resource])
            return resources

        return common_client(method, base_url, path, parameters, url, headers, data)
    
    return eventbrite_client
