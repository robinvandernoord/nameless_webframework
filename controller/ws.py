# EXAMPLE endpoints for WS

from framework.expose import websocket


# exposed at 'func'
@websocket
def func(server, *args):
    print('Func called with', args)
    server.js.some_func('hi')
    # you can send data back with server.send_client or return

    return {"random": "data"}
    # return js.some_func('bye')
    # return {'function': 'some_js_func', 'data': 'bye'}


@websocket()
def log(server, *args):
    print(*args)
    return {}


@websocket
def list_of_data(server, *args):
    return [1, 2, 4, 56]


# exposed at 'update_all'
@websocket('update_all')
def push_update(server, *a):
    # send an action to all connected peers
    for peer_code, peer in server.peers:
        # type(peer) == type(server)
        peer.send_client({'function': 'update'})
