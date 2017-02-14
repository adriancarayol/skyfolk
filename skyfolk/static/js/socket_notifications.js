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
                var message = '<li class=\"collection-item avatar\" data-id="'+ data.id +'">';
				message += '<a onclick="AJAX_mark_read(this)" class="fa fa-remove" id="mark-as-read-notification" data-notification="' + data.slug + '"/></a>';
            if (data.actor_avatar !== null && typeof data.actor_avatar !== 'undefined') {
                message = message + " <img class=\"circle\" src=\"" + data.actor_avatar + '"/>';
            }
            if(typeof data.actor !== 'undefined' && data.level !== 'new_follow'){
                message = message + "<a class=\"title\" href=\"/profile/" + data.actor + '" >' + data.actor + '</a>';
            }

            if(typeof data.verb !== 'undefined'){
                message = message + " <span class=\"title\"/>" + data.verb + '</span>';
            }

            if(typeof data.target !== 'undefined'){
                message = message + " " + item.target;
            }
            if(typeof data.description !== 'undefined' && data.description != null){
                message = message + " " + item.description;
            }
            if(typeof data.timestamp !== 'undefined'){
                message = message + "<p><i>" + data.timestamp + '</i></p>';
            }
            if (typeof data.level !== 'undefined' && data.level == 'friendrequest') {
                message = message + " <div class=\"notification-buttons\"><" +
'button data-notification="' + data.slug + '" onclick="AJAX_respondFriendRequest(\'' + data.actor_object_id + '\',\'' + "accept" + '\',\'' + data.id + '\'); AJAX_delete_notification(\'' + data.slug + '\',\'' + data.id + '\')" class="accept-response waves-effect waves-light btn white-text green"><i class="material-icons">done</i></button>\<' +
                    'button data-notification="' + data.slug + '" onclick="AJAX_respondFriendRequest(\'' + data.actor_object_id + '\',\'' + "rejected" + '\',\'' + data.id + '\'); AJAX_delete_notification(\'' + data.slug + '\',\'' + data.id + '\')" class="rejected-response waves-effect waves-light btn white-text red"> <i class="material-icons">cancel</i></button>\<' +
                    '/div>';
            }
            message += "<a href=\"#!\" class=\"secondary-content\"><i class=\"material-icons\">people<\/i><\/a></li>";
				// See if there's a div to replace it in, or if we should add a new one
                var list_notifications = $('#list-notify');
                var existing = $(list_notifications).find("[data-id='"+data.id+"']");
				/* Comprobamos si el elemento existe, si es asi lo modifcamos */
				if (existing.length) {
					existing.html(message);
				} else {
					$(list_notifications).prepend(message);
				}
			};

			// Helpful debugging
			if (socket.readyState == WebSocket.OPEN) socket.onopen();
			socket.onclose = function() { console.log("No connected."); };
		}
	};
}());
