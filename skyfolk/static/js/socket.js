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
                        if (data.level > 0) {
                            content += ' <div class="col s12 wrapper" id="pub-' + data.id + '" data-id="' + _args + '" style="min-width: 98% !important; border-right: 3px solid #1e88e5;">';
                        } else
                            content += ' <div class=\"col s12 wrapper\" id="pub-' + data.id + '" data-id="' + _args + '">';
                        content += "            <div class=\"box\">";
                        content += '            <span id="check-' + data.id + '" class=\"top-options zoom-pub tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Ver conversación completa\"><i class=\"fa fa-plus-square-o\" aria-hidden=\"true\"><\/i><\/span>';
                        if (_args == data.author_id && (data.event_type == 1 || data.event_type == 3)) {
                            content += '            <span data-id="' + data.id + '" id=\"edit-comment-content\" class=\"top-options edit-comment tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Editar comentario\"><i class=\"fa fa-pencil\" aria-hidden=\"true\"><\/i><\/span>';
                        }
                        content += '<div class="row">';
                        content += "                <div class=\"articulo col s12\">";
                        content += '<div class="row">';
                        if (_args == data.author_id) {
                            content += "      <div class=\"image col l1 m2 s2\" style=\"box-shadow: 0 1px 5px rgba(129, 199, 132, 1);\">";
                        } else {
                            content += "      <div class=\"image col l1 m2 s2\">";
                        }
                        content += '        <div class="usr-img img-responsive"><img src="' + data.avatar_path + '" alt="' + data.author_username + '" width="120" height="120"></div>';
                        content += "      </div>";
                        content += '<div class="col l10 m12 s9">';
                        content += '                  <h2 class="h22"><a href="/profile/' + data.author_username + '" >@' + data.author_username + '</a>';
                        if (data.parent) {
                            content += '<span class="chip">';
                            content += '<img src="' + data.parent_avatar + '" alt="'+data.author_parent+'">';
                            content += '<i class="fa fa-reply"></i> <a href="/profile/'+ data.parent_author +'">@'+ data.parent_author +'</a>';
                            content += '</span>';
                        }
                        content += '</h2>';
                        content += '                    <p id="pub-created" class="blue-text text-darken-2">' + data.created + '<\/p><br>';
                        content += '<div class="row publication-content">';
                        content += "                  <div class=\"parrafo comment\">";
                        content += '                      <div class="wrp-comment">' + data.content + '<\/div>';
                        content += "                  </div>";
                        content += '                    <div class="show-more" id="show-comment-' + data.id + '">';
                        content += "                        <a href=\"#\">+ Mostrar más<\/a>";
                        content += "                    </div>";
                        content += "                    </div>";
                        if (data.extra_content) {
                            content += '<div class="card small">';
                            content += '<div class="card-image">';
                            if (data.extra_content_image) {
                                content += '<img src="'+data.extra_content_image+'">';
                            } else {
                                content += '<img src="/static/dist/img/nuevo_back.png">';
                            }
                            content += '<span class="card-title white-text">' + data.extra_content_title + '</span>';
                            content += '</div>';
                            content += '<div class="card-content">';
                            content += '<p>' + data.extra_content_description + '</p>';
                            content += '</div>';
                            content += '<div class="card-action">';
                            content += '<a href="' + data.extra_content_url + '">Ver</a>';
                            content += '</div></div>';
                        }
                        if (typeof(data.images) !== 'undefined' && data.images !== null && data.images.length > 0) {
                            content += '<div class="row images">';
                            for(var image = 0; image < data.images.length; image++) {
                                content += '<div class="col s4 z-depth-2">';
                                content += '<img class="responsive-img" src="/media/'+data.images[image].image+'" alt="Imagen de: '+data.author_username+'" title="Imagen de: '+data.author_username+'">';
                                content += "                    </div>";
                            }  
                            content += "                    </div>";
                        }
                        content += "                    </div>";
                        content += "                    </div>";
                        content += "                    </div>";
                        content += "                    </div>";
                        content += '<div class="row">';
                        content += '<div class="divider"></div>';
                        content += "                <div class=\"options_comentarios\" id=\"options-comments\">";
                        content += "                    <ul class=\"opciones\">";
                        if (_args == data.board_owner_id || data.author_id == _args) {
                            content += "                             <li class=\"trash-comment\" title=\"Borrar comentario\"><i class=\"fa fa-trash\"><\/i><\/li>";
                        }
                        content += "                            <li title=\"No me gusta\" class=\"hate-comment\" id=\"fa-hate\">";
                        content += '                                <i class="fa fa-angle-down" aria-hidden="true"></i>';
                        content += '                                <i class="fa hate-value"></i>';
                        content += "                            </li>";
                        content += '                        <li id="like-heart" title="¡Me gusta!" class="like-comment"><i class="fa fa-angle-up" aria-hidden="true"></i><i id="like-value" class="fa"></i></li>';
                        content += '                       <li title=\"Añadir a mi skyline\" data-id="' + data.id + '" class=\"add-timeline\" id=\"add_to_skyline\"><i class=\"fa fa-quote-right\" aria-hidden=\"true\"> <\/i><\/li>';
                        content += '                       <li title="Responder" class="reply-comment"><i class="fa fa-reply" id="reply-caja-comentario-' + data.id + '"><\/i><\/li>';
                        content += "                    </ul>";
                        content += "                </div>";
                        content += "                </div>";
                        content += "    </div>";
                        if (_args == data.author_id) {
                            content += '<div data-user-id="' + data.author_id + '" id="author-controls-' + data.id + '" class="author-controls">';
                            content += '<div class="row">';
                            content += '<div class="col s12">';
                            content += '<form method="post" accept-charset="utf-8">';
                            content += '<input type="hidden" name="csrfmiddlewaretoken" value="' + data.token + '">';
                            content += '<div class="row">';
                            content += '<div class="input-field col s12">';
                            content += '<i class="material-icons prefix">create</i>';
                            content += '<textarea class="materialize-textarea" placeholder="Escribe el contenido del nuevo mensaje" id="id_caption-' + data.id + '" cols="40" maxlength="500" name="content" rows="10" required="required" style="height: 10.9969px;"></textarea>';
                            content += '<label for="id_caption-' + data.id + '">Editar comentario</label></div>';
                            content += '<div class="row">';
                            content += '<button data-id="' + data.id + '" class="waves-effect waves-light btn blue darken-1 right edit-comment-btn" type="button" id="submit_edit_publication">Editar<i class="material-icons right">mode_edit</i></button>';
                            content += '</div></div></form></div></div></div>';
                        }
                        content += '<div class="wrapper-reply">';
                        content += '<div class="hidden" id="caja-comentario-' + data.id + '">';
                        content += '<form class="reply-form" action="" method="post">';
                        content += '<input type="hidden" name="csrfmiddlewaretoken" value="' + data.token + '">';
                        content += '<input id="id_author" name="author" type="hidden" value="' + _args + '">';
                        content += '<input id="id_board_owner" name="board_owner" type="hidden" value="' + data.board_owner_id + '">';
                        content += '<input id="id_parent" name="parent" type="hidden">';
                        content += '<div class="row">';
                        content += '<div class="col s12">';
                        content += '<div class="row">';
                        content += '<div class="input-field col s12">';
                        content += '<textarea class="materialize-textarea message-reply" id="message-reply-' + data.id + '" cols="40" maxlength="500" name="content" placeholder="Responder a @' + data.author_username + '" rows="10" required=""></textarea>';
                        content += '<label for="message-reply-' + data.id + '">Escribe tu mensaje aqui...</label>';

                        content += '</div>';
                        content += '<div class="file-field input-field col s12">';
                        content += '<div class="btn">';
                        content += '<span>Imágenes</span>';
                        content += '<input id="id_image_reply" name="image" type="file" multiple>';
                        content += '</div>';
                        content += '<div class="file-path-wrapper">';
                        content += '<input class="file-path validate" type="text" placeholder="Upload one or more files">';
                        content += '</div></div></div></div></div>';
                        content += '<button type="button" id="reply-' + data.id + '" class="waves-effect waves-light btn right blue enviar">Enviar<i class="material-icons right">send</i></button>';
                        content += '</form></div></div>';
                        content += "    </div></div></div>";
                    }
                    // See if there's a div to replace it in, or if we should add a new one
                    var existing = $('#pub-' + data.id);
                    var no_comments = $('#without-comments');

                    /* Comprobamos si el elemento existe, si es asi lo modificamos */
                    if (existing.length) {
                        existing.find('#pub-created').first().text(data.created);
                        existing.find('.wrp-comment').first().text(data.content);
                    } else {
                        var parent = $('#pub-' + data.parent);
                        if (parent.length) {
                            if (data.level == 1 || data.level == 2) {
                                var children_list = $(parent).find('.children').first();
                                if (!children_list.length) {
                                    children_list = $(parent).find('.wrapper-reply').after('<ul class="children"></ul>');
                                }
                                $(children_list).prepend(content);
                            } else {
                                $(parent).closest('.row').after(content);
                            }
                        } else $("#tab-comentarios .btn-filters").after(content);
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
                } else if (data.type === "video") {
                    var existing_pub = $('#pub-' + data.id);
                    if (existing_pub.length) {
                        var card_content = $(existing_pub).find('.publication-content');
                        var videos = $(existing_pub).find('.videos');
                        if (videos.length) {
                            $(videos).append('<div class="col s4"><video class="responsive-video" controls loop><source src="/media/'+data.video+'" type="video/mp4"></video></div>');
                        } else {
                            var images = $(existing_pub).find('.images');
                            if (images.length) {
                                $(images).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="/media/'+data.video+'" type="video/mp4"></video></div></div>');
                            }
                            $(card_content).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="/media/'+data.video+'" type="video/mp4"></video></div></div>');
                        }
                    }
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
