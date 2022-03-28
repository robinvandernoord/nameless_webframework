# functions for exposing web endpoints

from twisted.web.resource import Resource
from twisted.web.static import File
from jinja2 import Environment, FileSystemLoader
from .config import encode
import json

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
        super().__init__(*a, **kw)

    def render(self, *a, **kw):
        res = super().render(*a, **kw)
        self.trigger_func(*a, **kw)
        return res


class Template(Resource):
    def __init__(self, template, func):
        super().__init__()
        self.template = template
        self.function = func

    def render(self, request):
        ctx = self.function(request)
        ctx["__globals"] = json.dumps(ctx)
        env = Environment(loader=FileSystemLoader('view'))
        template = env.get_template(f'{self.template}.html')
        output_from_parsed_template = template.render(**ctx)
        return encode(output_from_parsed_template)


def expose_static(alias=None, template=True):
    def decorator(func):
        def wrapper():
            name = func.__name__

            filename = name if template in (True, False, None) else template
            file = TriggerFile(func, f'view/{filename}.html')

            if alias and not callable(alias):
                where = alias
            else:
                where = name

            if template:
                contents = Template(filename, func)
            else:
                contents = file

            root.putChild(where.encode(), contents)

        return wrapper()

    if callable(alias):
        return decorator(alias)  # return 'wrapper'
    else:
        return decorator  # ... or 'decorator'


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

        request_method = method[0].lower() if method else 'get'
        if request_method == 'post':
            _add_page(root, f.__name__, function_post=f)
        elif request_method == 'get':
            _add_page(root, f.__name__, function_get=f)
        else:
            raise NotImplementedError('todo: other methods')
        return inner_wrapper

    return wrapper
