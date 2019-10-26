# EXAMPLE endpoints for WS

from framework.ws import expose_ws

# exposed at 'func'
@expose_ws()
def func(server, *args):
    print('Func called with', args)
    # server.send_client({'function': 'some_js_func', 'data': 'bye'})
    # you can send data back with server.send_client or return
    return {'function': 'some_js_func', 'data': 'bye'}


# exposed at 'update_all'
@expose_ws('update_all')
def push_update(server, *a):
    # send an action to all connected peers
    for peer_code, peer in server.peers:
        # type(peer) == type(server)
        peer.send_client({'function': 'update'})
