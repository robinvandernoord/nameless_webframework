# EXAMPLE endpoints for WS

from framework.expose import websocket

# exposed at 'func'
from framework.ws import functions, Server, Client


@websocket
def func(args, client: Client):
    print('Func called with', args)

    client.some_func(args)
    # you can send data back with server.send_client or return

    return {"random": "data"}


@websocket()
def log(args):
    print(*args)



@websocket
def list_of_data(args):
    a = args[0] if args else 0
    return [a, a + 1, a + 2, a * 2]


@websocket
def string(_):
    """
    Return a random string
    """
    return "something"


@websocket
def query_functions(_):
    return {name: method.__doc__ for name, method in functions.items()}


# exposed at 'update_all'
@websocket('update_all')
def push_update(server: Server):
    # send an action to all connected peers
    for peer_code, peer in server.peers:
        # type(peer) == type(server)
        peer.send_client({'function': 'update'})
