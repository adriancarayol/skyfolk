var UTILS = UTILS || (function(){
    var _args = {};

    return {
        init : function(args) {
            _args = args;
        },
        conn_socket : function() {
            // Correctly decide between ws:// and wss://
                var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
                var ws_path = ws_scheme + '://' + window.location.host + window.location.pathname + "stream/";
                console.log("Connecting to " + ws_path);
                var socket = new ReconnectingWebSocket(ws_path);

                // Handle incoming messages
                socket.onmessage = function(message) {
                    // Decode the JSON
                    console.log("Got message " + message.data);
                    var data = JSON.parse(message.data);
                    // Create the inner content of the post div
                if (data.type === "pub") {
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
                    content += "                    <div class=\"show-more\">";
                    content += "                        <a href=\"#\">+ Mostrar más<\/a>";
                    content += "                    </div>";
                    content += "              <!-- OPCIONES DE COMENTARIOS -->";
                    content += "                <div class=\"optiones_comentarios\">";
                    content += "                    <ul class=\"opciones\">";
                    content += "        ";
                    content += "                             <li class=\"trash-comment\" title=\"Borrar comentario\"><i class=\"fa fa-trash\"><\/i><\/li>";
                    content += "                            <li title=\"No me gusta\" class=\"fa-stack hate-with-values\" id=\"fa-hate\">";
                    content += "                                <span class=\"hate-comment\">";
                    content += "                                    <i class=\"fa fa-heart fa-stack-1x\"><\/i>";
                    content += "                                    <i class=\"fa fa-bolt fa-stack-1x fa-inverse\"><\/i>";
                    content += "                                    <i class=\"fa hate-value\"> 0<\/i>";
                    content += "                                </span>";
                    content += "                            </li>";
                    content += "                        <li title=\"¡Me gusta!\" class=\"like-comment\"><i id=\"like-heart\" class=\"fa fa-heart\"> 0<\/i><\/li>";
                    content += "                       <li title=\"Citar\" class=\"quote-comment\"><i class=\"fa fa-quote-left\">";
                    content += "                       <\/i><\/li>";
                    content += "                       <li title=\"Responder\" class=\"reply-comment\"><i class=\"fa fa-reply\" id=\"reply-caja-comentario-{{ pub.pk }}\"><\/i><\/li>";
                    content += "                       <li title=\"Añadir a mi timeline\" class=\"add-timeline\"><i class=\"fa fa-tag\"> 0<\/i><\/li>";
                    content += "                    </ul>";
                    content += "                </div>";
                    content += "                </div>";
                    content += "                <div class=\"wrapper-reply\">";
                    content += "";
                    content += "                <!-- RESPUESTAS A COMENTARIOS -->";
                    content += "";
                    content += "                <div class=\"comment-reply\">";
                    content += '                <div class=\"avatar-reply\"><img src="' + data.avatar_path + '" alt="' + data.author_username + '" width="120" height="120"><\/div>';
                    content += "                    <div class=\"author-reply\">";
                    content += "                      <a href=\"\/profile\/{{ reply.author }}\">author_reply<\/a>";
                    content += "                      <i class=\"reply-created\">created_reply<\/i>";
                    content += "                    </div>";
                    content += "                      <div class=\"content-reply\">reply_content<\/div>";
                    content += "                </div>";
                    content += "";
                    content += "                </div>";
                    content += "    </div>";
                    // See if there's a div to replace it in, or if we should add a new one
                    var existing = $('#pub-'+data.id);
                    if (existing.length) {
                        existing.html(content);
                    } else {
                        $("#tab-comentarios").prepend(content);
                    }
                }
                else
                    {
                        var content = "";
                        content += "                <div class=\"wrapper-reply\">";
                        content += "";
                        content += "                <!-- RESPUESTAS A COMENTARIOS -->";
                        content += "";
                        content += "                <div class=\"comment-reply\">";
                        content += '                <div class=\"avatar-reply\"><img src="' + data.avatar_path + '" alt="' + data.author_username + '" width="120" height="120"><\/div>';
                        content += "                    <div class=\"author-reply\">";
                        content += '                      <a href="/profile/'+data.author_username+'">'+data.author_username+'</a>';
                        content += '                      <i class="reply-created">'+data.created+'<\/i>';
                        content += "                    </div>";
                        content += '                      <div class="content-reply">'+data.content+'</div>';
                        content += "                </div>";
                        content += "";
                        content += "                </div>";
                        content += "    </div>";

                        var pub = $('#pub-'+data.parent);
                        $(pub).append(content);
                    }
                };

                // Helpful debugging
                socket.onopen = function() { console.log("Connected!"); };
                socket.onclose = function() { console.log("No connected."); };
        }
    };
}());