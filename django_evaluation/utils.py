from django.contrib.auth.decorators import login_required
from django.conf import settings

def settings_login_required(url):
    """
    
    """
    def _method_wrapper(function):
        def _wrapper(request, *args, **kwargs):
            menu_entries = settings.MENU_ENTRIES
            result = {}
            result['required'] = True
            res = filter(lambda menu_entries: menu_entries['url'] == url, menu_entries)
            if len(res) > 0:
                result['required'] = res[0].get('required',True)
            if not result['required']:
                return function(request, *args, **kwargs)
            else:
                return login_required(function)(request)
        _wrapper.__doc__ = function.__doc__
        _wrapper.__name__ = function.__name__
        return _wrapper
    return _method_wrapper

