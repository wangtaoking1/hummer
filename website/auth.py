from website.communicate import Communicator

def is_authenticated(request):
    cookies = {'sessionid': request.COOKIES.get('sessionid', None)}
    client = Communicator(cookies=cookies)
    ok, username = client.is_authenticated()
    return ok


def login_required():
    pass
