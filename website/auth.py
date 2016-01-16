from django.conf import settings
from functools import wraps
import logging

from django.http import HttpResponseRedirect

from website.communicate import Communicator

logger = logging.getLogger('website')


def is_authenticated(request):
    """
    Check that the user is authenticated, return is_login and username if
    necessary.
    """
    cookies = {'sessionid': request.COOKIES.get('sessionid', None)}
    client = Communicator(cookies=cookies)
    ok, username = client.is_authenticated()
    return ok, username


def login_required(login_url=None):
    """
    Decorator for views that checks that the user is authenticated, redirecting
    to login_url page if necessary.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            is_login, username = is_authenticated(request)
            if is_login:
                kwargs['username'] = username
                return view_func(request, *args, **kwargs)

            resolved_login_url = (login_url or settings.LOGIN_URL)
            return HttpResponseRedirect(resolved_login_url)
        return _wrapped_view
    return decorator
