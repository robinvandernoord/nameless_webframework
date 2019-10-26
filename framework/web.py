# functions for exposing web endpoints

from twisted.web.resource import Resource
from twisted.web.static import File
from .config import encode

__all__ = ['expose_static', 'expose_web', 'root']


def HTTP_CODE(code, message='', request=None):
    if request:
        request.setResponseCode(code)
    return encode(f'{message}')


# we server static files under "/view"
root = File("view")


class TriggerFile(File):
    def __init__(self, trigger_func, *a, **kw):
        self.trigger_func = trigger_func
        super(TriggerFile, self).__init__(*a, **kw)

    def render(self, *a, **kw):
        res = super(TriggerFile, self).render(*a, **kw)
        self.trigger_func(*a, **kw)
        return res


def expose_static(*method):
    def wrapper(f):
        name = f.__name__
        root.putChild(name.encode(), TriggerFile(f, f'view/{name}.html'))
        if method:
            alias = method[0]
            root.putChild(alias.encode(), TriggerFile(f, f'view/{name}.html'))

    return wrapper


def _safe_execute(func, request):
    try:
        return encode(func(request))
    except Exception as e:
        return HTTP_CODE(400, f'Something went wrong: {e}', request)


def _add_page(root, name, function_post=None, function_get=None):
    class Page(Resource):
        def render_POST(self, request):
            if not function_post:
                return HTTP_CODE(405, "Method 'POST' not allowed.", request)
            return _safe_execute(function_post, request)

        def render_GET(self, request):
            if not function_get:
                return HTTP_CODE(405, "Method 'GET' not allowed.", request)
            return _safe_execute(function_get, request)

    root.putChild(name.encode(), Page())


def expose_web(*method):
    def wrapper(f):
        def inner_wrapper(*a, **kw):
            f(*a, **kw)

        request_method = method[0]
        if request_method == 'post':
            _add_page(root, f.__name__, function_post=f)
        elif request_method == 'get':
            _add_page(root, f.__name__, function_get=f)
        else:
            raise NotImplementedError('todo: other methods')
        return inner_wrapper

    return wrapper
