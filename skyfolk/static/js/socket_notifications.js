var UTILS_N = UTILS_N || (function(){
	var _args = {};
	var _showLimitChar = 90;
	return {
		init : function(args) {
			_args = args;
		},
		conn_socket : function() {
			// Correctly decide between ws:// and wss://
			var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
			var ws_path = ws_scheme + '://' + window.location.host + window.location.pathname + "notification/";
			console.log("Connecting to " + ws_path);
			var socket = new ReconnectingWebSocket(ws_path);

			// Handle incoming messages
			socket.onmessage = function(message) {
				// Decode the JSON
				console.log("Got message " + message.data);
				var data = JSON.parse(message.data);
				// Create the inner content of the post div
				var content = "";
				content += '<div class="alert alert-block alert-'+data.level+'">prueba notificacion';
				content += '<a title="Borrar notificacion" class="close pull-right href="#">';
				content += '<i class="fa fa-trash" aria-hidden="true"></i></a>';
				content += '<a title="Marcar como leido" class="close pull-right" href="#">';
				content += '<i class="fa fa-eye-slash" aria-hidden="true"></i></a>';
				content += '<h5><i class="fa fa-bell" aria-hidden="true"></i>';
				if (data.level === "new_follow") {
					content += '<a href="#">'+data.actor+'</a>';
				}
				content += '<b>'+data.verb+'</b></h5>';
				content += '<p class="notice-timesince">'+data.timeline+'</p>';
				if (data.description) {
					content += '<p class="notice-description">'+data.description+'</p>';
				}
				if (data.level === "friendrequest") {
					content += '<div class="notification-buttons">';
					content += '<button data-notification="'+data.slug+'" class="accept-response">Rechazar</button>';
				content += '</div>';
				}
				content += '<div class="notice-actions">';
				content += '<a class="btn" href="#">'+data.title+'</a></div>';
				content += '</div>';
				// See if there's a div to replace it in, or if we should add a new one
				var existing = $('#notification-'+data.id);
				var no_comments = $('#without-comments');
				var comment_length = data.content.replace(/\s\s+/g, ' ');
				/* Comprobamos si el elemento existe, si es asi lo modifcamos */
				if (existing.length) {
					existing.html(content);
				} else {
					$("#notification-menu").prepend(content);
				}
				var show = $('div#pub-'+data.id+'').find('#show-comment-'+data.id+'');
				/* Eliminamos el div de "Este perfil no tiene comentarios" */
				if ($(no_comments).is(':visible')) {
					$(no_comments).fadeOut();
				}

				/* Comprobamos la longitud del nuevo comentario */
				if (comment_length.length < _showLimitChar) {
					$(show).css('display','none');
				}

			};

			// Helpful debugging
			if (socket.readyState == WebSocket.OPEN) socket.onopen();
			socket.onclose = function() { console.log("No connected."); };
		}
	};
}());
