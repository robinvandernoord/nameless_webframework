import sys

from framework import log, WebSocketServerFactory, reactor, Server, WebSocketResource, root, Site, ssl, config
from framework._autoreload import autoreload

# import pages and endpoints:
import controller.web
import controller.ws


def _create_listener(port, site_root, ssl_factory):
    if ssl_factory:
        return reactor.listenSSL(int(port), Site(site_root), ssl_factory)
    else:
        return reactor.listenTCP(int(port), Site(site_root))


def serve(arguments):
    if not arguments:
        port = '8080'
    else:
        port = arguments[0]
    log.startLogging(sys.stdout)
    if config.get('ssl'):
        factory = WebSocketServerFactory(u"wss://127.0.0.1:{}".format(port))
        ssl_factory = ssl.DefaultOpenSSLContextFactory('keys/privkey.pem',
                                                       'keys/cert.pem')
    else:
        factory = WebSocketServerFactory("ws://127.0.0.1:{}".format(port))
        ssl_factory = None

    factory.protocol = Server

    # run our WebSocket server under "/ws" (note that Twisted uses bytes for URIs)
    root.putChild(b"ws", WebSocketResource(factory))
    # start listening
    _create_listener(port, root, ssl_factory)
    reactor.run()


def main(*args):
    autoreload(serve, args)


if __name__ == '__main__':
    main(sys.argv[1:])
