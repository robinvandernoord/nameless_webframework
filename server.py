import sys

from framework import log, WebSocketServerFactory, reactor, Server, WebSocketResource, root, Site, ssl, config

# import pages and endpoints:
import controller.web
import controller.ws


def serve(arguments):
    if not arguments:
        port = '8080'
    else:
        port = arguments[0]
    log.startLogging(sys.stdout)
    if config['ssl']:
        factory = WebSocketServerFactory(u"wss://127.0.0.1:{}".format(port))
        ssl_factory = ssl.DefaultOpenSSLContextFactory('keys/privkey.pem',
                                                       'keys/cert.pem')
        #            port, site, ssl_factory
        listener = lambda p, s, sf: reactor.listenSSL(int(p), s, sf)
    else:
        factory = WebSocketServerFactory("ws://127.0.0.1:{}".format(port))
        listener = lambda p, s, _: reactor.listenTCP(int(p), s)
        ssl_factory = None

    factory.protocol = Server
    resource = WebSocketResource(factory)

    # and our WebSocket server under "/ws" (note that Twisted uses
    # bytes for URIs)
    root.putChild(b"ws", resource)
    site = Site(root)
    listener(port, site, ssl_factory)
    reactor.run()


if __name__ == '__main__':
    serve(sys.argv[1:])
