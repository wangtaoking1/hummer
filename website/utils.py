from django.conf import settings


def get_api_server_url(path):
    """
    Return the url for api server.
    """
    return "http://" + settings.API_SERVER + path
