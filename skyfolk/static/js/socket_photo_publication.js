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
                    var existing = $('#publication-thread').find('#pub-' + data.id).first();
                    var no_comments = $('#without-comments');

                    /* Comprobamos si el elemento existe, si es asi lo modificamos */
                    if (existing.length) {
                        existing.closest('.row-pub').replaceWith(data.content);
                    } else {
                        var parent = $('#pub-' + data.parent_id);
                        if (parent.length) {
                            $('#publication-thread').append(data.content);
                        } else if (data.parent_id === 'undefined') {
                            $("#publication-thread").append(data.content);
                        }
                    }
                    /* Comprobamos la longitud del nuevo comentario */
                } else if (data.type === "video") {
                    var existing_pub = $('#pub-' + data.id);
                    if (existing_pub.length) {
                        var card_content = $(existing_pub).find('.comment').next();
                        var videos = $(existing_pub).find('.videos');
                        if (videos.length) {
                            $(videos).append('<div class="col s4"><video class="responsive-video" controls loop><source src="'+data.video+'" type="video/mp4"></video></div>');
                        } else {
                            var images = $(existing_pub).find('.images');
                            if (images.length) {
                                $(images).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="'+data.video+'" type="video/mp4"></video></div></div>');
                            }
                            $(card_content).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="'+data.video+'" type="video/mp4"></video></div></div>');
                        }
                    }
                }
                $('.dropdown-button').dropdown();
                 $('.materialboxed').materialbox();
            };

            // Helpful debugging
            if (socket.readyState == WebSocket.OPEN) socket.onopen();
            socket.onclose = function () {
                console.log("No connected.");
            };
        }
    };
}());

