# EXAMPLE endpoints for HTTP


from framework.config import config
from framework.web import expose_web, expose_static


# beta will be an alias for index, index.html will be rendered
@expose_static('beta')
def index(request):
    # because 'index' is special, this function will only be called when you visit /beta
    print('beta called')


# you can also expose POST
@expose_web('get')
def admin(request):
    token = request.args.get(b'token')
    if token and token[0] == config.get('admintoken', '').encode():
        # auth
        return "you're in!"
    else:
        raise ValueError('invalid security token')

