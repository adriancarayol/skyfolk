var max_height_comment = 60;

var UTILS = UTILS || (function () {
    var _args = {};
    var _showLimitChar = 90;
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
                    var existing = $('#pub-' + data.id);
                    var no_comments = $('#without-comments');
                    no_comments.remove();
                    /* Comprobamos si el elemento existe, si es asi lo modificamos */
                    if (existing.length) {
                        existing.closest('.row').replaceWith(data.content);
                    } else {
                        var $parent = $('#pub-' + data.parent_id);
                        if ($parent.length) {
                            if (data.level == 1 || data.level == 2) {
                                var $children_list = $parent.find('.children').first();
                                if (!$children_list.length) {
                                    $children_list = $parent.find('.wrapper-reply').after('<ul class="children"></ul>');
                                }
                                $children_list.prepend(data.content);
                            } else {
                                $parent.closest('.row').after(data.content);
                            }
                        } else if (data.parent_id == null) {
                            $("#messages-wrapper").prepend(data.content);
                        }
                    }

                }   else if (data.type === "video") {
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
                } else {
                    var content = "";
                    content += "                <div class=\"wrapper-reply\">";
                    content += "";
                    content += "";
                    content += "                <div class=\"comment-reply\">";
                    content += '                <div class=\"avatar-reply\"><img src="' + data.avatar_path + '" alt="' + data.p_author_username + '" width="120" height="120"><\/div>';
                    content += "                    <div class=\"author-reply\">";
                    content += '                      <a href="/profile/' + data.p_author_username + '">' + data.p_author_username + '</a>';
                    content += '                      <i class="reply-created">' + data.created + '<\/i>';
                    content += "                    </div>";
                    content += '                      <div class="content-reply">' + data.content + '</div>';
                    content += "                </div>";
                    content += "";
                    content += "                </div>";
                    content += "    </div>";

                    var pub = $('#pub-' + data.parent);
                    $(pub).append(content);
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
