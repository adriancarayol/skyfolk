var UTILS = UTILS || (function () {
        var _args = {};
        var _max_height_comment = 60;
        return {
            init: function (args) {
                _args = args;
            },
            conn_socket: function () {
                // Correctly decide between ws:// and wss://
                var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
                var ws_path = ws_scheme + '://' + window.location.host + window.location.pathname + "stream/";
                console.log("Connecting to " + ws_path);
                var socket = new ReconnectingWebSocket(ws_path);

                // Handle incoming messages
                socket.onmessage = function (message) {
                    // Decode the JSON
                    console.log("Got message " + message.data);
                    var data = JSON.parse(message.data);
                    // Create the inner content of the post div
                    if (data.type === "pub") {
                        if (!data.is_edited) {
                            var content = "";
                            content += '<div class="row">';
                            content += '<div class="col s12">';
                            if (data.level > 0 && data.level < 3) {
                                content += ' <div class="col s12 wrapper" id="pub-' + data.id + '" data-id="' + _args + '" style="min-width: 98% !important;">';
                            } else
                                content += ' <div class=\"col s12 wrapper\" id="pub-' + data.id + '" data-id="' + _args + '">';
                            content += "            <div class=\"box\">";
                            content += '            <span id="check-' + data.id + '" class=\"top-options zoom-pub tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Ver conversación completa\"><i class=\"fa fa-plus-square-o\" aria-hidden=\"true\"><\/i><\/span>';
                            content += '            <span data-id="' + data.id + '" id=\"edit-comment-content\" class=\"top-options edit-comment tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Editar comentario\"><i class=\"fa fa-pencil\" aria-hidden=\"true\"><\/i><\/span>';
                            content += '<div class="row">';
                            content += "                <div class=\"articulo col s12\">";
                            content += '<div class="row">';
                            content += "      <div class=\"image col l1 m2 s2\">";
                            content += '        <div class="usr-img img-responsive"><img src="' + data.avatar_path + '" alt="' + data.author_username + '" width="120" height="120"></div>';
                            content += "      </div>";
                            content += '<div class="col l8 m12 s8">';
                            content += '                  <h2 class="h22"><a href="/profile/' + data.author_username + '" >@' + data.author_username + '</a></h2>';
                            content += '                    <a target="_blank">' + data.created + '<\/a><br>';
                            content += '<div class="row">';
                            content += "                  <div class=\"parrafo comment\">";
                            content += '                      <div class="wrp-comment">' + data.content + '<\/div>';
                            content += "                  </div>";
                            content += '                    <div class="show-more" id="show-comment-' + data.id + '">';
                            content += "                        <a href=\"#\">+ Mostrar más<\/a>";
                            content += "                    </div>";
                            content += "                    </div>";
                            content += "                    </div>";
                            content += "                    </div>";
                            content += "                    </div>";
                            content += "                    </div>";
                            content += '<div class="row">';
                            content += '<div class="divider"></div>';
                            content += "                <div class=\"options_comentarios\" id=\"options-comments\">";
                            content += "                    <ul class=\"opciones\">";
                            content += "        ";
                            content += "                             <li class=\"trash-comment\" title=\"Borrar comentario\"><i class=\"fa fa-trash\"><\/i><\/li>";
                            content += "                            <li title=\"No me gusta\" class=\"fa-stack\" id=\"fa-hate\">";
                            content += "                                <span class=\"hate-comment\">";
                            content += "                                    <i class=\"fa fa-heart fa-stack-1x\"><\/i>";
                            content += "                                    <i class=\"fa fa-bolt fa-stack-1x fa-inverse\"><\/i>";
                            content += "                                    <i class=\"fa hate-value\"><\/i>";
                            content += "                                </span>";
                            content += "                            </li>";
                            content += '                        <li id="like-heart" title="¡Me gusta!" class="like-comment"><i class="fa fa-heart"></i><i id="like-value" class="fa"></i></li>';
                            content += "                       <li title=\"Citar\" class=\"quote-comment\"><i class=\"fa fa-quote-left\">";
                            content += "                       <\/i><\/li>";
                            content += '                       <li title="Responder" class="reply-comment"><i class="fa fa-reply" id="reply-caja-comentario-' + data.id + '"><\/i><\/li>';
                            content += "                       <li title=\"Añadir a mi skyline\" class=\"add-timeline\" id=\"add_to_skyline\"><i class=\"fa fa-tag\"> <\/i><\/li>";
                            content += "                    </ul>";
                            content += "                </div>";
                            content += "                </div>";
                            content += "    </div>";
                            content += "    </div>";
                        }
                        // See if there's a div to replace it in, or if we should add a new one
                        var existing = $('#pub-' + data.id);
                        var no_comments = $('#without-comments');

                        /* Comprobamos si el elemento existe, si es asi lo modifcamos */
                        if (existing.length) {
                            existing.find('#pub-created').first().text(data.created);
                            existing.find('.wrp-comment').first().text(data.content);
                        } else {
                            var parent = $('#pub-' + data.parent);
                            if (parent.length) {
                                var children_list = $(parent).find('.children').first();
                                if (!children_list.length) {
                                    children_list = $(parent).find('.wrapper-reply').after('<ul class="children"></ul>');
                                }
                                $(children_list).prepend(content);
                            } else $("#tab-comentarios").prepend(content);
                        }
                        var show = $('div#pub-' + data.id + '').find('#show-comment-' + data.id + '');
                        /* Eliminamos el div de "Este perfil no tiene comentarios" */
                        if ($(no_comments).is(':visible')) {
                            $(no_comments).fadeOut();
                        }
                        var wrapper_content = $('#pub-' + data.id + '').find('.wrp-comment');
                        /* Comprobamos la longitud del nuevo comentario */
                        if ($(wrapper_content).height() > _max_height_comment) {
                            $(wrapper_content).css('height', '2.6em');
                        } else {
                            $(show).css('display', 'none');
                        }
                    }
                    /*else if (data.type === "reply" && !data.is_edited) {
                     var content = "";
                     content += "                <div class=\"wrapper-reply\">";
                     content += "";
                     content += "                <!-- RESPUESTAS A COMENTARIOS -->";
                     content += "";
                     content += "                <div class=\"comment-reply\">";
                     content += '                <div class=\"avatar-reply\"><img src="' + data.avatar_path + '" alt="' + data.author_username + '" width="120" height="120"><\/div>';
                     content += "                    <div class=\"author-reply\">";
                     content += '                      <a href="/profile/' + data.author_username + '">' + data.author_username + '</a>';
                     content += '                      <i class="reply-created">' + data.created + '<\/i>';
                     content += "                    </div>";
                     content += '                      <div class="content-reply">' + data.content + '</div>';
                     content += "                </div>";
                     content += "";
                     content += "                </div>";
                     content += "    </div>";

                     var pub = $('#pub-' + data.parent);
                     $(pub).append(content);
                     }*/
                };

                // Helpful debugging
                if (socket.readyState == WebSocket.OPEN) socket.onopen();
                socket.onclose = function () {
                    console.log("No connected.");
                };
            }
        };
    }());
