from base64 import b64encode

from .common import common_client, GET

def get_prestashop_client(access_key:str, base_url:str):
    headers = {
        'Authorization': 'Basic {}'.format(b64encode(f"{access_key}:".encode('ascii')).decode("ascii")),
        'Io-Format': 'JSON'
    }
    def prestashop_client(method, path, parameters=None, url=None, data=None, resource=False):
        if method.lower() == GET and resource:
            has_more_items = True
            index = 0
            number = 50
            resources = []
            while has_more_items:
                paged_parameters = {
                    **(parameters or {}),
                    'limit': f"{index},{number}"
                }

                result = common_client(GET, base_url, path=path, parameters=paged_parameters, headers=headers)
                resource_page = result.get(resource, [])
                has_more_items = len(resource_page) == number
                index += number
                resources.extend(resource_page)
            return resources

        else:
            response = common_client(method, base_url, path, parameters, url, headers, data)
            if response:
                # set result to the content of the only key of the response, eg:
                #   {'products': [...]}
                results = response[list(response)[0]]
            else:
                # if the response is falsey (eg.: [], None, ''...)
                results = response

        return results
    return prestashop_client
