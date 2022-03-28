// JS functions

// https://github.com/arlac77/svelte-websocket-store/blob/master/src/index.mjs#L43

function now() {
    return new Date();
}

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

function send(data) {
    let guid = undefined;
    if (typeof data == 'object') {
        guid = crypto.randomUUID();
        data['return'] = guid;
    }

    const _send = () => socket.send(JSON.stringify(data));
    if (socket.readyState !== WebSocket.OPEN) open().then(_send);
    else _send();

    return guid ? promise_ws(guid) : null;
}

// functions
let functions = {};
let promises = {};

export function expose(f) {
    functions[f.name] = f;
}

export const expose_function = expose;

function promise_ws(return_id) {
    let _p = {
        'created_at': now()
    };

    const p = new Promise(function (resolve, reject) {
        _p['resolve'] = resolve;
        _p['reject'] = reject;
    });

    _p['promise'] = p;

    promises[return_id] = _p;
    return p;
}

// 1 minute:
const EXPIRE_PROMISES = 1000 * 60;

async function cleanup_old_promises() {
    const n = now();
    for (let id of Object.keys(promises)) {
        const prom = promises[id];

        if (n - prom.created_at > EXPIRE_PROMISES) {

            console.log('purging', id, n - prom.created_at);

            delete promises[id];
        }
    }
}

function handle(data) {
    let response;

    try {
        response = JSON.parse(data);

        if (response['return']) {
            promises[response['return']].resolve(response.data ?? response);

            delete promises[response['return']];  // cleanup
        }

        console.log(promises);

    } catch (e) {
        throw data;
    } finally {
        cleanup_old_promises();
    }

    // if no error:

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