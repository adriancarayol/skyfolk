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

        /* Comprobamos si el elemento existe, si es asi lo modificamos */
        if (existing.length) {
            existing.replaceWith(data.content);
        } else {
            var parent = $('#pub-' + data.parent_id);
            if (parent.length) {
                parent.after(data.content);
            } else $(".theme-publications").prepend(data.content);
        }
    } else if (data.type === "video") {
        var existing_pub = $('#pub-' + data.id);
        if (existing_pub.length) {
            var card_content = $(existing_pub).find('.comment').next();
            var videos = $(existing_pub).find('.videos');
            if (videos.length) {
                $(videos).append('<div class="col s4"><video class="responsive-video" controls loop><source src="/media/' + data.video + '" type="video/mp4"></video></div>');
            } else {
                var images = $(existing_pub).find('.images');
                if (images.length) {
                    $(images).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="/media/' + data.video + '" type="video/mp4"></video></div></div>');
                }
                $(card_content).after('<div class="row videos"><div class="col s4"><video class="responsive-video" controls loop><source src="/media/' + data.video + '" type="video/mp4"></video></div></div>');
            }
        }
    }
};

// Helpful debugging
if (socket.readyState == WebSocket.OPEN) socket.onopen();
socket.onclose = function () {
    console.log("No connected.");
};


