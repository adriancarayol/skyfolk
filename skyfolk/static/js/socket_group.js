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
                var data = JSON.parse(message.data);
                // Create the inner content of the post div
                if (data.type === "pub") {
                    // See if there's a div to replace it in, or if we should add a new one
                    var existing = $('#pub-' + data.id);
                    var no_comments = $('#without-comments');

                    /* Comprobamos si el elemento existe, si es asi lo modificamos */
                    if (existing.length) {
                        existing.replaceWith(data.content);
                    } else {
                        var $parent = $('#pub-' + data.parent_id);
                        if ($parent.length) {
                            if (data.level === 1 || data.level === 2) {
                                var $children_list = $parent.find('.children').first();
                                if (!$children_list.length) {
                                    $children_list = $parent.find('.wrapper-reply').after('<ul class="children"></ul>');
                                }
                                $children_list.prepend(data.content);
                            } else {
                                $parent.closest('.row').after(data.content);
                            }
                        } else if (data.parent_id == null) {
                            $("#tab-comentarios").prepend(data.content);
                        }
                    }
                    /* Eliminamos el div de "Este perfil no tiene comentarios" */
                    if ($(no_comments).is(':visible')) {
                        $(no_comments).fadeOut(function() {
                            $(this).remove();
                        });
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
                } else if (data.type === "theme") {
                    var $theme_list = $(".theme-list");
                    var existing_theme = $theme_list.find(`[data-id='${data.id}']`);
                    if (existing_theme.length) {
                        existing_theme.replaceWith(data.theme);
                    } else {
                        $theme_list.prepend(data.theme);
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
