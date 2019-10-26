# [NO NAME YET]

## Web framework based on Autobahn/Twisted

### How to use:
Install the requirements and run server.py.
Use the config to tweak some settings or make your own.

- Custom functions (non-exposed) go in model 
- Endpoints go in controler (web.py and ws.py for http and websocket respectively)
- HTML and static files go in 'view'
- SSL keys go in a folder 'keys' if you want to make a 'wss' connection

### Features
- Expose HTTP endpoints
- Expose web socket endpoints
- Expose static pages

### TODO
- Implement templating to make static pages less static
- Store data per connected peer
- More HTTP methods (currently only GET and POST are allowed)
- Better usage examples
- replace 1th with 1st