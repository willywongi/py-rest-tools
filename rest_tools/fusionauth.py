from rest_tools.common import common_client

DEFAULT_NUMBER_OF_RESULTS = 25


def get_fusionauth_client(base_url, api_key, number_of_results=DEFAULT_NUMBER_OF_RESULTS):
    headers = {'Authorization': api_key}
    def fusionauth_client(method, path="/", parameters=None, url=None, data=None, resource=None):
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
