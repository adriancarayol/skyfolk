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
				content += '  <div class=\"wrapper\" id="pub-' + data.id + '" data-id="' + _args + '">';
				content += "            <div class=\"box\">";
				content += '            <span id="check-' + data.id + '" class=\"zoom-pub\"><i class=\"fa fa-expand fa-lg\"><\/i><\/span>';
				content += "            <!-- Check para ampliar el mensaje... -->";
				content += '                  <div class=\"ampliado\" id="expand-' + data.id + '">';
				content += "                      <div class=\"cerrar_ampliado\"><i class=\"fa fa-close\"><\/i><\/div>";
				content += "                      <div class=\"nombre_image\">";
				content += "                    <ul>";
				content += '                      <li><i class="first">' + data.author_first_name + " " + data.author_last_name + '<\/i><\/li>';
				content += '                      <li><a class=\"name\" href="/profile/' + data.author_username + '">' + data.author_username + '<\/a><\/li>';
				content += "                    </ul>";
				content += '                    <div class="usr-img img-responsive"><img src="' + data.avatar_path + '" alt="' + data.author_username + '" width="120" height="120"></div>';
				content += "                      </div>";
				content += "                    <div class=\"parrafo comment-tab\">";
				content += "                     <a href=\"\/profile\/{{ pub.author.username }}\">{{pub.author.username}}<\/a>";
				content += '                        <a target="_blank">' + data.created + '</a><br><br>';
				content += data.content;
				content += "                    </div>";
				content += "                      <div class=\"wrapper-reply\">";
				content += "                        <!-- RESPUESTAS A COMENTARIOS -->";
				content += "                        <div class=\"comment-reply\">";
				content += '                        <div class="avatar-reply"><img src="' + data.avatar_path + '" alt="' + data.author_username + '" width="120" height="120"></div>';
				content += '                            <div class="author-reply"><span class="triangle"> <\/span><a href="/profile/' + data.author_username + '">' + data.author_username + '</a></div>';
				content += '                              <div class="content-reply">' + data.content + '<\/div>';
				content += "                        </div>";
				content += "                    </div>";
				content += "                  </div>";
				content += "      <div class=\"image\">";
				content += '        <div class="usr-img img-responsive"><img src="' + data.avatar_path + '" alt="' + data.author_username + '" width="120" height="120"></div>';
				content += "      </div>";
				content += "</div>";
				content += "";
				content += "                <div class=\"articulo\">";
				content += '                  <h2 class="h22"><a href="/profile/' + data.author_username + '" >' + data.author_username + '</a> ha comentado:  </h2>';
				content += "                  <div class=\"parrafo comment\">";
				content += '                    <a target="_blank">' + data.created + '<\/a><br>';
				content += '                      <div class="wrp-comment">' + data.content + '<\/div>';
				content += "                  </div>";
				content += '                    <div class="show-more" id="show-comment-'+data.id+'">';
				content += "                        <a href=\"#\">+ Mostrar más<\/a>";
				content += "                    </div>";
				content += "              <!-- OPCIONES DE COMENTARIOS -->";
				content += "                <div class=\"options_comentarios\" id=\"options-comments\">";
				content += "                    <ul class=\"opciones\">";
				content += "        ";
				content += "                             <li class=\"trash-comment\" title=\"Borrar comentario\"><i class=\"fa fa-trash\"><\/i><\/li>";
				content += "                            <li title=\"No me gusta\" class=\"fa-stack hate-with-values\" id=\"fa-hate\">";
				content += "                                <span class=\"hate-comment\">";
				content += "                                    <i class=\"fa fa-heart fa-stack-1x\"><\/i>";
				content += "                                    <i class=\"fa fa-bolt fa-stack-1x fa-inverse\"><\/i>";
				content += "                                    <i class=\"fa hate-value\"> <\/i>";
				content += "                                </span>";
				content += "                            </li>";
				content += "                        <li title=\"¡Me gusta!\" class=\"like-comment\"><i id=\"like-heart\" class=\"fa fa-heart\"> <\/i><\/li>";
				content += "                       <li title=\"Citar\" class=\"quote-comment\"><i class=\"fa fa-quote-left\">";
				content += "                       <\/i><\/li>";
				content += '                       <li title="Responder" class="reply-comment"><i class="fa fa-reply" id="reply-caja-comentario-'+data.id+'"><\/i><\/li>';
				content += "                       <li title=\"Añadir a mi timeline\" class=\"add-timeline\"><i class=\"fa fa-tag\"> <\/i><\/li>";
				content += "                    </ul>";
				content += "                </div>";
				content += "                </div>";
				content += "    </div>";
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
