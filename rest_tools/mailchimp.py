"""Mailchimp API tools.

API reference: https://mailchimp.com/developer/marketing/api/
"""
from base64 import b64encode
from io import BytesIO
from itertools import zip_longest
import logging
import json
import tarfile
import time
from typing import Any, Callable, Sequence

import requests

from .common import common_client, GET, POST


DEFAULT_COUNT = 10
DEFAULT_PATIENCE = 120  # seconds
logger = logging.getLogger('rest_tools.mailchimp')


def get_mailchimp_client(apikey:str, count:int=DEFAULT_COUNT) -> Callable:
    """Returns a callable you can use to interact with Mailchimp API.
    :param access_token: A apikey from your developer profile page
        (see: https://mailchimp.com/developer/marketing/docs/fundamentals/#authenticate-with-an-api-key)
    :param base_url: the default should be changed only if asked from Mailchimp
    """
    base_url = f"https://{apikey.split('-')[1]}.api.mailchimp.com/3.0"
    headers = {
        'Authorization': 'Basic {}'.format(b64encode("username:{}".format(apikey).encode('ascii')).decode("ascii"))
    }

    def mailchimp_client(method, path, parameters=None, url=None, data=None, resource=None):
        """REST tool to interact with Mailchimp API.

        The path parameters should always start with a "/" and should NOT include the version (eg: `/campaigns`)
        :param method: one of the HTTP verb (GET, POST, DELETE,...)
        :param path: the path of the resource (eg.: `/campaigns`)
        :param parameters: the optional query parameters that will be encoded in the querystring.
        :param url: if specified, path and parameters will be ignored (this should be a full URL, eg. `https://us6.api.mailchimp.com/3.0/campaigns`)
        :param data: the optional body content of a POST/PATCH/PUT request. It will be encoded as JSON.
        :param resource: if true & method is GET, the client will request all the paginated content (it will make 1+ requests as needed). 
        """
        if method.lower() == GET and resource:
            results = []
            offset = 0
            remainder = True
            while remainder:
                paging_parameters = dict(parameters) if parameters else {}
                paging_parameters.update({
                    'count': count,
                    'offset': offset
                })
                result = common_client(GET, base_url, path,
                                        parameters=paging_parameters,
                                        headers=headers)
                total_items = result['total_items']
                if total_items:
                    current_resources = result[resource]
                else:
                    current_resources = []
                remainder = total_items - len(current_resources) - offset
                results.extend(current_resources)
                if remainder:
                    offset = offset + count
            return results
        else:
            return common_client(method, base_url, path, parameters=parameters, url=url, headers=headers, data=data)
    
    return mailchimp_client


def get_mailchimp_batch(apikey:str, count:int=DEFAULT_COUNT, patience:int=DEFAULT_PATIENCE) -> Callable:
    mailchimp_client = get_mailchimp_client(apikey, count)

    def mailchimp_batch(operations:Sequence[Sequence[str, str, Any]]):
        ops = [{
            'method': method,
            'path': resource_path,
            'body': json.dumps(data)
        } for method, resource_path, data in operations]

        batch = mailchimp_client(POST, path="/batches", data={"operations": ops})

        response_body_url = None
        last_status = None
        while last_status != 'finished' and patience:
            update = mailchimp_client("get", f"/batches/{batch['id']}")
            last_status = update['status']
            if last_status == 'finished':
                response_body_url = update.get('response_body_url')
                break
            else:
                patience = patience - 1
                time.sleep(1)

        if not patience:
            raise TimeoutError(f"Timeout expired while waiting for batch operation {batch['id']}. Last status: {last_status}")

        if response_body_url:
            r = requests.get(response_body_url)

            with tarfile.open(fileobj=BytesIO(r.content), mode="r") as tar:
                results = ()
                for member in tar.getmembers():
                    if member.isfile() and member.size:
                        try:
                            results = json.load(tar.extractfile(member))
                        except Exception:
                            logger.exception("Unable to read response content from file %s", response_body_url)
                            continue
                for req, res in zip(ops, results):
                    if res['status_code'] != 200:
                        logger.error(
                            f"Request/{req['method']} on {req['path']} failed with {res['status_code']}. Response: {res['response']}")
        else:
            results = ()

        return zip_longest(operations, results)
    return mailchimp_batch
