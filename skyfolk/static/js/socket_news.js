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
				console.log("Got message " + message.data);
				var data = JSON.parse(message.data);
				// Create the inner content of the post div
				var content = '<div class=\"col l3 m12 s12\" data-id="' + data.id + '">';
				content += '<div class=\"notice-item\">';
				content += '<div class=\"col l3 m2 s3 img\">';
				content += '<img src="'+data.author_avatar+'"></div>';
				content += '<div class=\"col l8 m9 s8 author\">';
				content += '<a href=\"/profile/\"'+data.author_username+'>'+data.author_username+'</a><i>'+data.author_first_name + ' ' + data.author_last_name +'</i>';
				content += '<i class=\"pub-date\">'+data.created+'</i></div>';
				content += '<div class=\"col l9 m10 s9 contenido\"><p>'+data.content+'</p></div>';
				content += '</div></div>';
				// See if there's a div to replace it in, or if we should add a new one
				var list_notifications = $('#stream-publications');
				var existing = $(list_notifications).find("[data-id='" + message.id + "']");
				/* Comprobamos si el elemento existe, si es asi lo modifcamos */
				if (existing.length) {
					existing.html(content);
				} else {
					$(list_notifications).prepend(content);
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
