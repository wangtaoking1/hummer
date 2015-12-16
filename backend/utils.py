import os, json
import logging

logger = logging.getLogger('hummer')


def fetch_digest_from_response(response):
    """
    Fetch the image digest from response when push image from docker host to
    private registry.
    """
    res = json.loads(response.decode())
    items = res.get('status').split(' ')
    res = [item for item in items if item.startswith('sha256:')]
    digest = res[0].split(':')[-1]

    return digest

