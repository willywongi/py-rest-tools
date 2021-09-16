from datetime import datetime, timedelta
from functools import wraps
import json
import logging
from typing import Any, Mapping, Optional
from urllib.parse import urlencode

import requests


logger = logging.getLogger('rest_tools')
GET = "get"
POST = "post"
PUT = "put"
PATCH = "patch"
DELETE = "delete"


def cache(fn):
    """ Decorator that adds a cache to GET requests.
    """
    cache = {}
    def wrapper(method, base_url, path="/", parameters=None, url=None, **kwargs):
        use_cache = method.lower() == 'get'
        argk = (path, parameters if parameters is None else tuple(parameters.items()), url)
        result = cache.get(argk)

        if use_cache and result:
            return result
        else:
            return fn(method, base_url, path=path, parameters=parameters, url=url, **kwargs)
    
    return wrapper


def expiring(getter):
    """ This decorator employs a single cache on the wrapped fn that expires
        after the number of seconds that the `getter` fn returns.
    """
    def inner_fn(f):
        f.expiry = None
        f.result = None
        @wraps(f)
        def wrapper(*args, **kwargs):
            if f.result and f.expiry and f.expiry > datetime.now():
                return f.result
            f.result = f(*args, **kwargs)
            f.expiry = datetime.now() + timedelta(seconds=getter(f.result))
            return f.result
        return wrapper
    return inner_fn


def common_client(method: str, base_url: str, path:str="/", 
                    parameters:Optional[Mapping]=None, url:Optional[str]=None, headers:Optional[Mapping]=None, 
                    data:Any=None, form_data:Optional[Mapping]=None, files:Optional[Mapping]=None) -> Any:
    """Practical, common REST client. 

    :param method: the http verb (GET, POST, DELETE,...)
    :param base_url: eg. "www.example.com:8000"
    :param path: the path of the service (eg.: "/webhooks/")
    :param url: if set, replaces the base_url + path.
    :parame headers: headers dictionary to be sent.
    :param parameters: the optional dictionary for url parameters
    :param data: the optional json data to post
    :param form_data: the optional data (form urlencoded) to post
    :param files: the optional files to upload (via post)
    :returns: the parsed JSON response for the endpoint.
    """

    complete_url = get_complete_url(base_url, path, parameters=parameters, url=url)
    response = get_response(method, complete_url, headers=headers, data=data, form_data=form_data, files=files)
    contents = response.text
    if contents:
        result = json.loads(contents)
    else:
        result = None

    return result


def get_complete_url(base_url:str, path:str, parameters:Mapping=None, url:str=None) -> str:
    if url:
        complete_url = url
    else:
        complete_url = f"{base_url}{path}"

    if parameters:
        query = dict(parameters)
    else:
        query = {}

    if query:
        complete_url = f"{complete_url}?{urlencode(query, doseq=True)}"
    
    return complete_url


def get_response(method:str, url:str, headers:Mapping=None, 
                    data:Mapping=None, form_data:Mapping=None, files:Mapping=None) -> requests.Response:
    response = getattr(requests, method.lower())(url, headers=headers, json=data, data=form_data, files=files)
    logger.debug("Request %s on %s got %s", method, url, response.status_code)
    try:
        response.raise_for_status()
    except Exception:
        try:
            logger.error(response.json())
        except Exception:
            logger.error(response.text)
        raise
    return response
