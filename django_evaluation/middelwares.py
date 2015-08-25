from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import AnonymousUser


try:
    from threading import local, current_thread
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()


class GlobalUserMiddleware(object):
    """
    Sets the current authenticated user in threading locals

    Usage example:
        from app_name.middleware import get_current_user
        user = get_current_user()
    """
    def process_request(self, request):
        setattr(
            _thread_locals,
            'user_{0}'.format(current_thread().name),
            request.user)

    def process_response(self, request, response):

        key = 'user_{0}'.format(current_thread().name)

        if not hasattr(_thread_locals, key):
            return response

        delattr(_thread_locals, key)

        return response


def get_current_user():
    return getattr(
        _thread_locals,
        'user_{0}'.format(current_thread().name),
        None
    )
