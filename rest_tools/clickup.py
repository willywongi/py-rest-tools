"""ClickUp API Tools.

Guide: https://clickup.com/api
"""
from typing import Callable
from .common import common_client, GET


def get_clickup_client(api_token:str, base_url:str="https://api.clickup.com/api/v2") -> Callable:
    """Returns a callable you can use to interact with ClickUp API.
    :param api_token: A personal token from the `Apps` section in your User Settings.
        (see: https://jsapi.apiary.io/apis/clickup20/introduction/authentication/personal-token.html)
    :param base_url: the default should be changed only if asked from ClickUp
    """
    headers = {
        'Authorization': api_token,
        'Content-Type': "application/json"
    }
    def clickup_client(method, path, parameters=None, url=None, data=None):
        """REST tool to interact with Clickup API.

        The path parameters should always start with a "/" and should NOT include the version (eg: `/team`)
        :param method: one of the HTTP verb (GET, POST, DELETE,...)
        :param path: the path of the resource (eg.: `/team`)
        :param parameters: the optional query parameters that will be encoded in the querystring.
        :param url: if specified, path and parameters will be ignored (this should be a full URL, eg. `https://api.clickup.com/api/v2/team`)
        :param data: the optional body content of a POST/PATCH/PUT request. It will be encoded as JSON.
        """
        return common_client(method, base_url, path, parameters, url, headers, data)
    
    return clickup_client
