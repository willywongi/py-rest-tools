import json
from re import compile

from .common import get_complete_url, get_response, common_client


def get_canvas_client(base_url:str, access_token:str):
    headers = {'Authorization': f'Bearer {access_token}'}
    rx = compile(r"<(.*?)>; rel=\"(\w+)\"")
    def canvas_client(method, path="/", parameters=None, url=None, data=None, file_object=None, resource=None):
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
                                headers=headers, form_data=data, files={'file': file_object})
    return canvas_client
