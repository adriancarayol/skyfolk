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
                    var content = '<div class="wrapper" id="pub-' + data.id + '" data-id="'+ _args + '">\
                          <div id="box">\
                              <span id="check-' + data.id + '" class="zoom-pub"><i class="fa fa-expand fa-lg"></i></span>\
                              <div class="ampliado" id="expand-' + data.id +'">\
                                <div class="nombre_image">\
                                <ul>\
                                <li><i class="first">' + data.author_first_name + data.author_last_name + '</i></li>\
                                <li><a class="name" href="/profile/' + data.author_username + '" >' + data.author_username + '</a></li>\
                                </ul>\
                                <img src="' + data.avatar_path + '" alt="img" class="usr-img img-responsive">\
                                </div>\
                                <div class="parrafo comment-tab">\
                                <a target="_blank">' + data.created + '</a><br><br>' + data.content + '\
                                </div>\
                                <div class="text_area">\
                                  <textarea placeholder="Escribe tu mensaje..."></textarea>\
                                  <div class="botones_ampliado">\
                                    <button class="enviar_ampliado"></i class="fa fa-paper-plane"></i>Enviar</button>\
                                    <button class="cerrar_ampliado"></i class="fa fa-close"></i><label for="check-' + data.id + '">Cerrar</label></button>\
                                    <button class="difundir_ampliado"></i class="fa fa-bullhorn"></i> Difundir mensaje</button>\
                                    <button class="foto_ampliado"></i class="fa fa-paperclip"></i> Añadir archivo</button>\
                                    <button class="localizacion_ampliado"></i class="fa fa-map-marker"></i> Añadir localización</button>\
                                  </div>\
                              </div>\
                              <div class="image">\
                              <img src="' + data.avatar_path + '" alt="img" class="usr-img img-responsive">\
                              </div>\
                              </div>\
                        </div>\
                        <article class="articulo">\
                          <h2 class="h22"><a href="/profile/' + data.author_username + '" >' + data.author_username + '</a> ha publicado: </h2>\
                          <div class="parrafo comment">\
                          <img src="' + data.avatar_path + '" alt="img" class="usr-img img-responsive">\
                            <a target="_blank">' + data.created + '</a><br>\
                            <div class="wrp-comment">' + data.content + '</div>\
                          </div>\
                          <div class="show-more">\
                            <a href="#">+ Mostrar más</a>\
                          </div>\
                          <div class="optiones_comentarios">\
                          </div>\
                        </article>\
                    </div>';

                    // See if there's a div to replace it in, or if we should add a new one
                    var existing = $("div[data-post-id=" + data.id + "]");
                    if (existing.length) {
                        existing.html(content);
                    } else {
                        $("#tab-comentarios").prepend(content);
                    }
                };

                // Helpful debugging
                socket.onopen = function() { console.log("Connected!"); };
                socket.onclose = function() { console.log("No connected."); };
        }
    };
}());