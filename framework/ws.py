# functions for exposing websocket endpoints

from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from .config import encode
import json

__all__ = ['expose_ws', 'peers', 'Server']

peers, functions = {}, {}


def expose_ws(*command):
    def wrapper(f):
        if command:
            cmd = command[0]
        else:
            cmd = f.__name__

        def inner_wrapper(*a, **kw):
            f(*a, **kw)

        functions[cmd] = f
        return inner_wrapper

    return wrapper


class Server(WebSocketServerProtocol):

    @property
    def peers(self):
        return peers.items()

    @staticmethod
    def default_func(_):
        raise NotImplementedError('please query another method ({})'.format(list(functions)))

    @staticmethod
    def payload_to_dict(pl):
        return json.loads(pl.decode())

    def send_client(self, message):
        self.sendMessage(encode(message))

    def _handle(self, payload):
        payload = self.payload_to_dict(payload)
        function = functions.get(payload.get('function', None), self.default_func)
        result = function(self, payload.get('data', {}))
        return encode(result)

    def onConnect(self, request):
        # add peer to peer pool
        peers[request.peer] = self

    def onMessage(self, payload, is_binary):
        try:
            self.send_client(self._handle(payload))
        except Exception as e:
            self.send_client('An error occured: {}'.format(str(repr(e))))

    def onClose(self, was_clean, code, reason):
        if peers.get(self.peer):
            # cleanup
            del peers[self.peer]
