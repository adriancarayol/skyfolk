var UTILS_E = UTILS_E || (function () {
	var _args = {};
	var _showLimitChar = 90;
	return {
		init: function (args) {
			_args = args;
		},
		conn_socket: function () {
			// Correctly decide between ws:// and wss://
			var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
			var ws_path = ws_scheme + '://' + window.location.host + window.location.pathname + "news/";
			console.log("Connecting to " + ws_path);
			var socket = new ReconnectingWebSocket(ws_path);

			// Handle incoming messages
			socket.onmessage = function (message) {
				// Decode the JSON
				console.log("Got message " + message.data);
				var data = JSON.parse(message.data);
				// Create the inner content of the post div
				var content = '<a class=\"collection-item avatar\" data-id="' + data.id + '">NUEVO</a>';
				// See if there's a div to replace it in, or if we should add a new one
				var list_notifications = $('#list-notify');
				var existing = $(list_notifications).find("[data-id='" + data.id + "']");
				/* Comprobamos si el elemento existe, si es asi lo modifcamos */
				if (existing.length) {
					existing.html(content);
				} else {
					$(list_notifications).prepend(content);
					var live_notify = $('#live_notify_badge');
					$(live_notify).html(parseInt($(live_notify).html(), 10)+1);
				}
			};

			// Helpful debugging
			if (socket.readyState == WebSocket.OPEN) socket.onopen();
			socket.onclose = function () {
				console.log("No connected.");
			};
		}
	};
}());
