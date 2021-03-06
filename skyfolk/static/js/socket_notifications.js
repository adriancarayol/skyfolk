var UTILS_N = UTILS_N || (function () {
    var _args = {};
    var _showLimitChar = 90;
    return {
        init: function (args) {
            _args = args;
        },
        conn_socket: function () {
            // Correctly decide between ws:// and wss://
            var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
            var ws_path = ws_scheme + '://' + window.location.host + window.location.pathname + "notification/";
            console.log("Connecting to " + ws_path);
            var socket = new ReconnectingWebSocket(ws_path);

            // Handle incoming messages
            socket.onmessage = function (message) {
                // Decode the JSON
                var data = JSON.parse(message.data);
                // See if there's a div to replace it in, or if we should add a new one
                var list_notifications = $('#list-notify');
                var existing = $(list_notifications).find("[data-id='" + data.id + "']");
                /* Comprobamos si el elemento existe, si es asi lo modifcamos */
                if (existing.length) {
                    existing.replaceWith(data.content);
                } else {
                    $(list_notifications).prepend(data.content);
                    var live_notify = $('#live_notify_badge');
                    $(live_notify).html(parseInt($(live_notify).text(), 10) + 1);
                }
                Materialize.toast($(data.content).find('.title'), 4000);
            };

            // Helpful debugging
            if (socket.readyState == WebSocket.OPEN) socket.onopen();
            socket.onclose = function () {
                console.log("No connected.");
            };
        }
    };
}());
