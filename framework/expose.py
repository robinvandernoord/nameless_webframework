from functools import partial

from framework.ws import expose_ws
from framework.web import expose_web
from framework.web import expose_static

__all__ = ["websocket", "web", "static", "template"]

websocket = expose_ws
web = expose_web
template = expose_static

static = partial(template, template=False)
