// JS functions


// constants
const TIMEOUT_TIMES = 10; // how often reconnect to server
const TIMEOUT_WAIT = 1000;  // how long wait before reconnect to server
const LOG = 1; // enable or disable log
let ellog;
if (LOG) {
    ellog = document.getElementById('log');
}

function start_conn(e, iteration) {
    log('welcome');
    if (!iteration) {
        iteration = 1;
    }
    if (iteration > TIMEOUT_TIMES) {
        // try if the whole page is down
        window.location.reload();
    }

    let wsuri;
    if (window.location.protocol === "file:") {
        wsuri = "ws://127.0.0.1:8080/ws?a=23&foo=bar";
    } else {
        let port = window.location.port ? `:${window.location.port}` : '';  // default not needed with nginx configured for ws
        let protocol = window.location.protocol === 'http:' ? 'ws' : 'wss';
        wsuri = `${protocol}://${window.location.hostname}${port}/ws?a=23&foo=bar`;
    }

    if ("WebSocket" in window) {
        sock = new WebSocket(wsuri);
    } else if ("MozWebSocket" in window) {
        // noinspection JSUnresolvedFunction
        sock = new MozWebSocket(wsuri);
    } else {
        log("Browser does not support WebSocket!");
    }

    if (sock) {
        sock.onopen = function () {
            log("Connected to " + wsuri);
            log(`(for the ${iteration}th time)`);
        };

        sock.onmessage = function (e) {
            handle(e.data);
        };

        sock.onclose = function (e) {
            log("Connection closed (wasClean = " + e.wasClean + ", code = " + e.code + ", reason = '" + e.reason + "')");
            sock = null;
            // retry after 1 second
            log('retrying in 1 second...');
            setTimeout(function (e) {
                start_conn(e, iteration + 1);
            }, TIMEOUT_WAIT);
        };
    }
}


let sock = null;

window.onload = start_conn;

let callbacks = {};

function promise_ws(return_id) {
    return new Promise(function (resolve, reject) {
        // executor (the producing code, "singer")
        let i = 0;
        const int = setInterval(function () {
            if (callbacks[return_id]) {
                clearInterval(int);
                return resolve(callbacks[return_id])
            } else {
                i++;
                if(i > 200){
                    clearInterval(int);
                    return reject('timeout')
                }
            }
        }, 100);
    });
}

function send(msg) {
    let guid = undefined;
    if (typeof msg == 'object') {
        guid = Date.now();
        msg['return'] = guid;
        callbacks[guid] = 0;
    }
    if (typeof msg != 'string') {
        msg = JSON.stringify(msg)
    }
    if (sock) {
        sock.send(msg);
        log("Sent " + msg);
        return guid ? promise_ws(guid) : null;
    } else {
        log("Not connected. (retrying now)");
        start_conn(null, 1);
        setTimeout(function () {
            send(msg)
        }, TIMEOUT_WAIT)
    }
}

// function disconnect() {
//     sock = null;
// }

function log(m) {
    if (LOG) {
        ellog.innerHTML += m + '\n';
        ellog.scrollTop = ellog.scrollHeight;
    }
    console.info(m)
}


// functions
let functions = {};

function expose_function(f) {
    functions[f.name] = f
}

function handle(data) {
    let response;
    try {
        response = JSON.parse(data);
        if (response['return'] && callbacks[response['return']] === 0) {
            callbacks[response['return']] = response;
        }
    } catch (e) {
        throw data;
    }
    if (response && response['function'] && functions[response['function']]) {
        return functions[response['function']](response.data)
    } else {
        log(response)
    }
}


if (LOG) {
    document.querySelector('#log').style.display = null
}


const _handler_func = {
    apply(_, __, args) {
        let result = send({'function': this._python_func, 'data': args})
        this._python_func = null;
        return result;
    },
    get(f, python_func) {
        // f is just there to placehold the function class
        if (python_func.startsWith('_')) {
            // internal function, use regular get
            return this[python_func]
        } else {
            this._python_func = python_func;
            return new Proxy(f, _handler_func);
        }
    },
};

const python = new Proxy(() => 0, _handler_func);

function update() {
    window.location.reload();
}

expose_function(update);