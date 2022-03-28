# EXAMPLE endpoints for HTTP


from framework.config import config
from framework.expose import web, static, template
from framework.web import Request, Args


# beta will be an alias for index, index.html will be rendered
@static('beta')
def index(request: Request):
    # because 'index' is special, this function will only be called when you visit /beta
    print('beta called', request)


@template
def a_template():
    return {'some': 'data'}


@template(template='a_template')
def an_other_template():
    return {'some': 'other data'}


@template(template='svelte/index')
def svelte():
    return {'name': 'Earth'}


# you can also expose POST
@web('get')
def admin(request: Request, args: Args):
    token = args.get(b'token')

    print(request.args, args, token, config.get('admintoken'))

    if token and token[0] == config.get('admintoken', '').encode():
        # auth
        return "you're in!"
    else:
        raise ValueError('invalid security token')
