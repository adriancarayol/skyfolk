var UTILS_E = UTILS_E || (function () {
	var _args = {};
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
				var data = JSON.parse(message.data);
				// Create the inner content of the post div
				var list_notifications = $('#stream-publications');
				var existing = $(list_notifications).find("[data-id='" + message.id + "']");
				/* Comprobamos si el elemento existe, si es asi lo modifcamos */
				if (existing.length) {
					existing.replaceWith(data.content);
				} else {
					$(list_notifications).prepend(data.content);
				}
                var $grid = $('.grid').masonry();
                $grid.imagesLoaded().progress( function() {
                    $grid.masonry('reloadItems');
                    $grid.masonry('layout');
                });
			};

			// Helpful debugging
			if (socket.readyState == WebSocket.OPEN) socket.onopen();
			socket.onclose = function () {
				console.log("No connected.");
			};
		}
	};
}());
