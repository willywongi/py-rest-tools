"""Fusionauth API tools.

API overview: https://fusionauth.io/docs/v1/tech/apis/
"""
from rest_tools.common import common_client

DEFAULT_NUMBER_OF_RESULTS = 25


def get_fusionauth_client(api_key:str, base_url:str, number_of_results:int=DEFAULT_NUMBER_OF_RESULTS):
    """Returns a callable you can use to interact with Fusionauth API.
    :param api_key: the api key, see: https://fusionauth.io/docs/v1/tech/apis/authentication/#api-key-authentication
    :param base_url: the url of your Fusionauth instance
    """
    headers = {'Authorization': api_key}
    def fusionauth_client(method, path="/", parameters=None, url=None, data=None, resource=None):
        """REST tool to interact with Fusionauth API.

        The path parameters should always start with a "/" and should include the word "api" (eg: `/api/user`)
        :param method: one of the HTTP verb (GET, POST, DELETE,...)
        :param path: the path of the resource (eg.: `/api/user`)
        :param parameters: the optional query parameters that will be encoded in the querystring.
        :param url: if specified, path and parameters will be ignored (this should be a full URL, eg. `https://fusionauth.example.com/api/user`)
        :param data: the optional body content of a POST/PATCH/PUT request. It will be encoded as JSON.
        :param resource: if this is a string & method is GET, the client will request all the paginated content (it will make 1+ requests as needed). 
        """
        if method == "get" and resource:
            start_row = 0
            resources = []
            while True:
                paged_parameters = dict(parameters) if parameters else {}
                if start_row != 0:
                    paged_parameters['startRow'] = start_row
                if number_of_results != DEFAULT_NUMBER_OF_RESULTS:
                    paged_parameters['numberOfResults'] = number_of_results
                result = common_client(method, base_url, path=path, 
                                        parameters=paged_parameters, headers=headers)
                if result['total'] == 0:
                    break
                resources.extend(result[resource])
                if len(resources) < result['total']:
                    start_row += number_of_results
                else:
                    break
            return resources
            
        return common_client(method, base_url, path=path, parameters=parameters, data=data, url=url, 
                                headers=headers)
    return fusionauth_client
