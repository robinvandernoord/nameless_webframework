// JS functions

// https://github.com/arlac77/svelte-websocket-store/blob/master/src/index.mjs#L43
const reopenTimeouts = [2000, 5000, 10000, 30000, 60000];

let socket, openPromise, reopenTimeoutHandler;
let reopenCount = 0;
const subscriptions = new Set();

function reopenTimeout() {
    const n = reopenCount;
    reopenCount++;
    return reopenTimeouts[
        n >= reopenTimeouts.length - 1 ? reopenTimeouts.length - 1 : n
        ];
}

function reopen() {
    close();
    if (subscriptions.size > 0) {
        reopenTimeoutHandler = setTimeout(() => open(), reopenTimeout());
    }
}

async function open() {
    if (reopenTimeoutHandler) {
        clearTimeout(reopenTimeoutHandler);
        reopenTimeoutHandler = undefined;
    }

    // we are still in the opening phase
    if (openPromise) {
        return openPromise;
    }

    let wsuri;
    if (window.location.protocol === "file:") {
        wsuri = "ws://127.0.0.1:8080/ws?a=23&foo=bar";
    } else {
        let port = window.location.port ? `:${window.location.port}` : '';  // default not needed with nginx configured for ws
        let protocol = window.location.protocol === 'http:' ? 'ws' : 'wss';
        wsuri = `${protocol}://${window.location.hostname}${port}/ws?a=23&foo=bar`;
    }

    socket = new WebSocket(wsuri);

    socket.onmessage = e => {
        handle(e.data);
    };

    socket.onclose = _ => reopen();

    openPromise = new Promise((resolve, reject) => {
        socket.onerror = error => {
            reject(error);
            openPromise = undefined;
        };
        socket.onopen = _ => {
            reopenCount = 0;
            resolve();
            openPromise = undefined;
        };
    });
    return openPromise;
}

open();

class TO_BE_FILLED_IN {
}

function promise_ws(return_id) {
    return new Promise(function (resolve, reject) {
        // todo: resolve callbacks differently (without interval etc.)

        // executor (the producing code, "singer")
        let i = 0;
        const int = setInterval(function () {

            if (callbacks[return_id] !== TO_BE_FILLED_IN) {
                clearInterval(int);
                return resolve(callbacks[return_id]);
            } else {
                i++;
                if (i > 200) {
                    clearInterval(int);
                    return reject('timeout');
                }
            }
        }, 100);
    });
}

function send(data) {
    let guid = undefined;
    if (typeof data == 'object') {
        guid = crypto.randomUUID();
        data['return'] = guid;
        callbacks[guid] = TO_BE_FILLED_IN;
    }

    const _send = () => socket.send(JSON.stringify(data));
    if (socket.readyState !== WebSocket.OPEN) open().then(_send);
    else _send();

    return guid ? promise_ws(guid) : null;
}

// functions
let functions = {};
let callbacks = {};

export function expose(f) {
    functions[f.name] = f;
}

export const expose_function = expose;

function handle(data) {
    let response;


    try {
        response = JSON.parse(data);

        if (response['return'] && callbacks[response['return']] === TO_BE_FILLED_IN) {
            callbacks[response['return']] = response.data ?? response;
        }
    } catch (e) {
        throw data;
    }

    if (response && response['function'] && functions[response['function']]) {
        return functions[response['function']](response.data);
    }
}


const _handler_func = {
    apply(_, __, args) {
        let result = send({'function': this._python_func, 'data': args});
        this._python_func = null;
        return result;
    },
    get(f, python_func) {
        // f is just there to placehold the function class
        if (python_func.startsWith('_')) {
            // internal function, use regular get
            return this[python_func];
        } else {
            this._python_func = python_func;
            return new Proxy(f, _handler_func);
        }
    }
};


class Python {
    _proxy;

    constructor(value, handler) {
        this._proxy = this.__proto__.__proto__ = new Proxy(value, handler);
    }
}

export const python = new Python(_ => 0, _handler_func);

function update() {
    window.location.reload();
}

expose_function(update);