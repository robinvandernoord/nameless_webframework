# EXAMPLE endpoints for HTTP


from framework.config import config
from framework.expose import web, static, template


# beta will be an alias for index, index.html will be rendered
@static('beta')
def index(request):
    # because 'index' is special, this function will only be called when you visit /beta
    print('beta called')


@template
def a_template(request):
    return {'some': 'data'}


@template(template='a_template')
def an_other_template(request):
    return {'some': 'other data'}


# you can also expose POST
@web('get')
def admin(request):
    token = request.args.get(b'token')
    if token and token[0] == config.get('admintoken', '').encode():
        # auth
        return "you're in!"
    else:
        raise ValueError('invalid security token')
