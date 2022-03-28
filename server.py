import sys

from framework.server import serve

# import pages and endpoints:
import controller.web
import controller.ws



def main(*args):
    serve(args, dev=True)


if __name__ == '__main__':
    main(sys.argv[1:])
