import threading

_user = threading.local()


def get_current_user():
    """
    Returns the current user from the thread-local storage.
    """
    return getattr(_user, "value", None)


class CurrentUserMiddleware:
    """
    Middleware to set the current user in thread-local storage.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _user.value = request.user if request.user.is_authenticated else None
        response = self.get_response(request)
        _user.value = None
        return response
