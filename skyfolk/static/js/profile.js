var countFriendList = 1;
var flag_reply = false;
var max_height_comment = 60;

$(document).ready(function () {
    var tab_comentarios = $('#tab-comentarios');
    var tab_timeline = $('#tab-timeline');
    var tab_amigos = $('#tab-amigos');
    // var wrapper_timeline = $(tab_timeline).find('#wrapperx-timeline');
    var wrapper_shared_pub = $('#share-publication-wrapper');

    /* Show more - Show less */
    $(tab_comentarios).find('.wrapper').each(function () {
        var comment = $(this).find('.wrp-comment');
        var show = $(this).find('.show-more a');

        if ($(comment).height() > max_height_comment) {
            $(show).show();
            $(comment).css('height', '2.6em');
        } else {
            //$(show).css('display', 'none');
        }
    });

    $(tab_comentarios).on('click', '.show-more a', function () {
        var $this = $(this);
        var $content = $this.parent().prev("div.comment").find(".wrp-comment");
        var linkText = $this.text().toUpperCase();

        if (linkText === "+ MOSTRAR MÁS") {
            linkText = "- Mostrar menos";
            $content.css('height', 'auto');
        } else {
            linkText = "+ Mostrar más";
            $content.css('height', '2.6em');
        }
        $this.text(linkText);
        return false;
    });

    $(tab_timeline).find('.timeline-pub').each(function () {
        var comment = $(this).find('#timeline-id-content');
        var text = comment.text();
        var show = $(this).find('.show-more a');
        text = text.replace(/\s\s+/g, ' ');

        if (text.length < 90) {
            $(show).css('display', 'none');
        }
    });

    $(tab_timeline).on('click', '.show-more a', function () {
        var $this = $(this);
        var $content = $this.parent().prev("#timeline-id-content");
        var linkText = $this.text().toUpperCase();

        if (linkText === "+ MOSTRAR MÁS") {
            linkText = "- Mostrar menos";
            $content.css('height', 'auto');
        } else {
            linkText = "+ Mostrar más";
            $content.css('height', '2.6em');
        }
        $this.text(linkText);
        return false;
    });

    $('.fa-paw').on('click', function () {
        $(".info-paw").show();
    });

    $('.info-trof').on('click', function () {
        $(".trofeos").show();
    });

    $('.info-groups').on('click', function () {
        $(".grupos").show();
    });

    $('#close-trofeos').on('click', function () {
        $(".trofeos").hide();
    });

    $('#close-grupos').on('click', function () {
        $(".grupos").hide();
    });


    $('#configurationOnProfile').on('click', function () {
        var _ventana_pin = $('.ventana-pin');
        if ($(_ventana_pin).is(':visible')) {
            $('html, body').removeClass('body-inConf');
            $(_ventana_pin).fadeOut("fast");
        } else {
            $('html, body').addClass('body-inConf');
            $(_ventana_pin).fadeIn("fast");
        }
    });

    /* Abrir respuesta a comentario */
    $(tab_comentarios).on('click', '#options-comments .fa-reply', function () {
        var id_ = $(this).attr("id").slice(6);
        $("#" + id_).slideToggle("fast");
    });

    /* Editar comentario */
    $(tab_comentarios).on('click', '#edit-comment-content', function () {
        var id = $(this).attr('data-id');
        $("#author-controls-" + id).slideToggle("fast");
    });

    $(tab_comentarios).on('click', '#submit_edit_publication', function (event) {
        event.preventDefault();
        var id = $(this).attr('data-id');
        var content = $(this).closest('#author-controls-' + id).find('#id_caption-' + id).val();
        AJAX_edit_publication(id, content);
    });

    function replyComment(caja_pub) {
        var id_comment = $(caja_pub).attr('id').split('-')[1];
        var commentReply = document.getElementById('actual-' + id_comment);
        $(commentReply).toggleClass("reply-actual-message-show");
    }

    /* Expandir comentario */

    $(tab_comentarios).on('click', '.wrapper .zoom-pub', function () {
        var caja_pub = $(this).closest('.wrapper');
        expandComment(caja_pub);
    });

    function expandComment(caja_pub) {
        var id_pub = $(caja_pub).attr('id').split('-')[1];  // obtengo id
        window.location.href = '/publication/' + id_pub;
    }

    /* Cerrar comentario expandido */

    $('.cerrar_ampliado').on('click', function () {
        var expand = $(this).closest('.ampliado');
        closeExpand(expand);
    });

    function closeExpand(expand) {
        var c = $(expand).attr('id').split('-')[1];
        var toClose = document.getElementById('expand-' + c);
        $(toClose).hide();
    }

    /* Borrar publicacion */
    $(tab_comentarios).on('click', '#options-comments .fa-trash', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        swal({
            title: "Are you sure?",
            text: "You will not be able to recover this publication!",
            type: "warning",
            animation: "slide-from-top",
            showConfirmButton: true,
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Yes, delete it!",
            cancelButtonText: "No God, please no!",
            closeOnConfirm: true
        }, function (isConfirm) {
            if (isConfirm) {
                AJAX_delete_publication(caja_publicacion);
            }
        });
    });

    /* Agregar skyline */
    $(document).on('click', '#options-comments #add_to_skyline', function () {
        var tag = this;
        $(wrapper_shared_pub).attr('data-id', $(tag).attr('data-id'));
        $(wrapper_shared_pub).show();
    });

    /* Compartir a skyline */
    $(wrapper_shared_pub).find('#share_publication_form').on('submit', function (event) {
        event.preventDefault();
        var content = $(wrapper_shared_pub).find('#shared_comment_content').val();
        var pub_id = $(wrapper_shared_pub).attr('data-id');
        var tag = $('#pub-' + pub_id).find('.add-timeline').first();
        AJAX_add_timeline(pub_id, tag, content);
    });

    /* Cerrar div de compartir publicacion */
    $('#close_share_publication').click(function () {
        $(wrapper_shared_pub).hide();
    });

    /* Eliminar skyline */
    $(document).on('click', '#options-comments #remove_from_skyline', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var tag = this;
        AJAX_add_timeline($(caja_publicacion).attr('id').split('-')[1], tag, null);
    });

    /* Añadir me gusta a comentario */
    $(document).on('click', '#options-comments #like-heart', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        AJAX_add_like(caja_publicacion, heart, "publication");
    });

    /* Añadir no me gusta a comentario */
    $(document).on('click', '#options-comments #fa-hate', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        AJAX_add_hate(caja_publicacion, heart, "publication");
    });

    /* FUNCIONES AJAX PARA TABS DE PERFIL */

    /*$(tab_amigos).bind('scroll', function () {
     if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {
     countFriendList++;
     $.ajax({
     type: "POST",
     url: "/load_friends/",
     data: {
     'slug': countFriendList,
     'csrfmiddlewaretoken': csrftoken
     },
     dataType: "json",
     success: function (response) {

     //load friends
     for (var i = 0; i < response.length; i++) {
     addFriendToHtmlList(response[i]);
     }
     },
     error: function (rs, e) {

     }
     });
     }
     });*/


    /**/
    $("#li-tab-amigos").click(function () {
        $(tab_amigos).css({
            "overflow": "auto"
        });
    });

    $("#li-tab-comentarios").click(function () {
        $(tab_comentarios).css({
            "overflow": "auto"
        });

    });

    $("#li-tab-timeline").click(function () {
        $('#tab-timeline').css({
            "overflow": "auto"
        });
    });

    $('#personal-card-info').find('#bloq-user').on('click', function () {
        var obj = document.getElementById('info-user-name-profile'),
            username = obj.getAttribute('data-id'),
            buttonBan = $(this);
        swal({
            title: "Bloquear a " + username,
            text: username + " no podrá seguirte, enviarte mensajes ni ver tu contenido.",
            type: "warning",
            customClass: 'default-div',
            animation: "slide-from-top",
            showConfirmButton: true,
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Bloquear",
            cancelButtonText: "Cancelar",
            closeOnConfirm: true
        }, function (isConfirm) {
            if (isConfirm) {
                AJAX_bloq_user(buttonBan);
            }
        });
    });

    $(this).click(function (event) {
        var _personal_card_info = $('#personal-card-info');
        if (!$(event.target).closest('#personal-card-info').length) {
            if (!$(event.target).closest('.fa-paw').length) {
                if ($(_personal_card_info).is(":visible")) {
                    $(_personal_card_info).hide();
                }
            }
        }
    });

    /* LOAD MORE ON CLICK */
    $(tab_comentarios).on('click', '#load_more_publications', function () {
        var loader = $(this).next().find('#load_publications_descendants');
        $(loader).fadeIn();
        var last_pub = $(loader).closest('.row').prev('.children').find('.wrapper').last().attr('id');
        var last_pub_id = "";
        if (undefined !== last_pub && last_pub.length) {
            last_pub_id = last_pub.toString().split('-')[1];
        }
        AJAX_load_publications($(this).attr("data-id"), loader, last_pub_id, this);
        return false;
    });

    /* LOAD MORE SKYLINE ON CLICK */
    $(tab_comentarios).on('click', '#load_more_skyline', function () {
        var input_skyline = $(this);
        var loader = $(input_skyline).next().find('#load_publications_skyline');
        $(loader).fadeIn();
        AJAX_load_skyline(loader, input_skyline);
        return false;
    });
}); // END DOCUMENT READY */


var didScroll = false;

$(window).scroll(function () {
    if ($(window).scrollTop() == $(document).height() - $(window).height()) {
        didScroll = true;
    }
});

setInterval(function () {
    if (didScroll) {
        didScroll = false;
        var input_skyline = $('#load_more_skyline');
        var loader = $(input_skyline).next().find('#load_publications_skyline');
        $(loader).fadeIn();
        AJAX_load_skyline(loader, input_skyline);
    }
}, 250);


/*PETICION AJAX PARA 'I LIKE' DEL PERFIL*/
function AJAX_likeprofile(status) {
    if (status == "noabort") $.ajax({
        type: "POST",
        url: "/like_profile/",
        data: {
            'slug': $("#profileId").html(),
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (response) {
            var _likes = $('#likes').find('strong');
            if (response == "like") {
                $("#ilike_profile").css('color', '#ec407a');
                $(_likes).html(parseInt($(_likes).html()) + 1);
            } else if (response == "nolike") {
                $("#ilike_profile").css('color', '#46494c');
                if ($(_likes).html() > 0) {
                    $(_likes).html(parseInt($(_likes).html()) - 1);
                }
            } else if (response == "blocked") {
                swal({
                    title: "Vaya... algo no está bien.",
                    customClass: 'default-div',
                    text: "Si quieres dar un like, antes debes desbloquear este perfil.",
                    timer: 4000,
                    showConfirmButton: true,
                    type: "error"
                });
            } else {
                console.log("...");
            }
        },
        error: function (rs, e) {
            // alert(rs.responseText);
        }
    }); else if (status == "anonymous") {
        swal({
            title: "¡Ups!",
            text: "Debe estar registrado",
            customClass: 'default-div'
        });
    }

}

function add_loaded_publication(pub, data, btn, is_skyline) {
    var publications = JSON.parse(data);

    if (publications === undefined || publications.length <= 0) {
        if (is_skyline)
            $(btn).remove();
        return;
    }

    var existing = $('#pub-' + pub);
    var pub_to_add;

    if (undefined !== existing && existing.length && !is_skyline) {
        var children_list = $(existing).find('.children').first();
        if (undefined === children_list || !children_list.length) {
            children_list = $(existing).find('.wrapper-reply').after('<ul class="children"></ul>');
        }
        var content = "";
        var i;
        for (i = 0; i < publications.length; i++) {
            pub_to_add = $('pub-' + publications[i].id);
            if (undefined !== pub_to_add && pub_to_add.length) continue;

            content = '<div class="row">';
            content += '<div class="col s12">';
            if (publications[i].level > 0 && publications[i].level < 3) {
                content += ' <div class="col s12 wrapper" id="pub-' + publications[i].id + '" data-id="' + publications[i].user_id + '" style="min-width: 98% !important;">';
            } else
                content += ' <div class=\"col s12 wrapper\" id="pub-' + publications[i].id + '" data-id="' + publications[i].user_id + '">';
            content += "            <div class=\"box\">";
            content += '            <span id="check-' + publications[i].id + '" class=\"top-options zoom-pub tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Ver conversación completa\"><i class=\"fa fa-plus-square-o\" aria-hidden=\"true\"><\/i><\/span>';
            if (publications[i].user_id == publications[i].author_id && (publications[i].event_type == 1 || publications[i].event_type == 3)) {
                content += '            <span data-id="' + publications[i].id + '" id=\"edit-comment-content\" class=\"top-options edit-comment tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Editar comentario\"><i class=\"fa fa-pencil\" aria-hidden=\"true\"><\/i><\/span>';
            }
            content += '<div class="row">';
            content += "                <div class=\"articulo col s12\">";
            content += '<div class="row">';
            if (publications[i].user_id == publications[i].author_id) {
                content += '      <div class="image col l1 m2 s2" style="box-shadow: 0 1px 5px rgba(129, 199, 132, 1);">';
            } else {
                content += "      <div class=\"image col l1 m2 s2\">";
            }
            content += '        <div class="usr-img img-responsive"><img src="' + publications[i].author_avatar + '" alt="' + publications[i].author_username + '" width="120" height="120"></div>';
            content += "      </div>";
            content += '<div class="col l10 m12 s9">';
            content += '                  <h2 class="h22"><a href="/profile/' + publications[i].author_username + '" >@' + publications[i].author_username + '</a>';
            if (publications[i].parent) {
                content += '<span class="chip">';
                content += '<img src="' + publications[i].parent_avatar + '" alt="' + publications[i].parent_author + '">';
                content += '<i class="fa fa-reply"></i> <a href="/profile/' + publications[i].parent_author + '">@' + publications[i].parent_author + '</a>';
                content += '</span>';
            }
            content += '</h2>';
            content += '                    <p id="pub-created" class="blue-text text-darken-2">' + publications[i].created + '<\/p><br>';
            content += '<div class="row">';
            content += "                  <div class=\"parrafo comment\">";
            content += '                      <div class="wrp-comment">' + publications[i].content + '<\/div>';
            content += "                  </div>";
            content += '                    <div class="show-more" id="show-comment-' + publications[i].id + '">';
            content += "                        <a href=\"#\">+ Mostrar más<\/a>";
            content += "                    </div>";
            content += "                    </div>";
            if (publications[i].extra_content) {
                content += '<div class="card small">';
                content += '<div class="card-image">';
                if (publications[i].extra_content_image) {
                    content += '<img src="' + publications[i].extra_content_image + '">';
                } else {
                    content += '<img src="/static/dist/img/nuevo_back.png">';
                }
                content += '<span class="card-title white-text">' + publications[i].extra_content_title + '</span>';
                content += '</div>';
                content += '<div class="card-content">';
                content += '<p>' + publications[i].extra_content_description + '</p>';
                content += '</div>';
                content += '<div class="card-action">';
                content += '<a href="' + publications[i].extra_content_url + '">Ver</a>';
                content += '</div></div>';
            }
            if (publications[i].image) {
                                content += '<div class="row">';
                                content += '<div class="col s7">';
                                content += '<img class="responsive-img" src="'+publications[i].image+'" alt="Imagen de: '+publications[i].author_username+'" title="Imagen de: '+publications[i].author_username+'">';
            }
            content += "                    </div>";
            content += "                    </div>";
            content += "                    </div>";
            content += "                    </div>";
            content += '<div class="row">';
            content += '<div class="divider"></div>';
            content += "                <div class=\"options_comentarios\" id=\"options-comments\">";
            content += "                    <ul class=\"opciones\">";
            if (publications[i].user_id == publications[i].board_owner_id || publications[i].user_id == publications[i].author_id) {
                content += "                             <li class=\"trash-comment\" title=\"Borrar comentario\"><i class=\"fa fa-trash\"><\/i><\/li>";
            }
            if (publications[i].user_id != publications[i].author_id) {
                content += "                            <li title=\"No me gusta\" class=\"hate-comment\" id=\"fa-hate\">";
                content += '                                <i class="fa fa-angle-down" aria-hidden="true"></i>';
                content += '                                <i class="fa hate-value">'+ (publications[i].hates > 0 ? publications[i].hates : '') +'</i>';
                content += "                            </li>";
                content += '                        <li id="like-heart" title="¡Me gusta!" class="like-comment"><i class="fa fa-angle-up" aria-hidden="true"></i><i id="like-value" class="fa">'+ (publications[i].likes > 0 ? publications[i].likes : '') +'</i></li>';
            }
            content += '                       <li title="Añadir a mi skyline" data-id="'+publications[i].id+'" class="add-timeline" id="add_to_skyline"><i class="fa fa-quote-right" aria-hidden="true"> '+ (publications[i].shares > 0 ? publications[i].shares : '') +'</i></li>';
            content += '                       <li title="Responder" class="reply-comment"><i class="fa fa-reply" id="reply-caja-comentario-' + publications[i].id + '"><\/i><\/li>';
            content += "                    </ul>";
            content += "                </div>";
            content += "                </div>";
            content += "    </div>";
            if (publications[i].user_id == publications[i].author_id) {
                content += '<div data-user-id="' + publications[i].author_id + '" id="author-controls-' + publications[i].id + '" class="author-controls">';
                content += '<div class="row">';
                content += '<div class="col s12">';
                content += '<form method="post" accept-charset="utf-8">';
                content += '<input type="hidden" name="csrfmiddlewaretoken" value="' + publications[i].token + '">';
                content += '<div class="row">';
                content += '<div class="input-field col s12">';
                content += '<i class="material-icons prefix">create</i>';
                content += '<textarea class="materialize-textarea" placeholder="Escribe el contenido del nuevo mensaje" id="id_caption-' + publications[i].id + '" cols="40" maxlength="500" name="content" rows="10" required="required" style="height: 10.9969px;"></textarea>';
                content += '<label for="id_caption-' + publications[i].id + '">Editar comentario</label></div>';
                content += '<div class="row">';
                content += '<button data-id="' + publications[i].id + '" class="waves-effect waves-light btn blue darken-1 right edit-comment-btn" type="button" id="submit_edit_publication">Editar<i class="material-icons right">mode_edit</i></button>';
                content += '</div></div></form></div></div></div>';
            }
            content += '<div class="wrapper-reply">';
            content += '<div class="hidden" id="caja-comentario-' + publications[i].id + '">';
            content += '<form class="reply-form" action="" method="post">';
            content += '<input type="hidden" name="csrfmiddlewaretoken" value="' + publications[i].token + '">';
            content += '<input id="id_author" name="author" type="hidden" value="' + publications[i].user_id + '">';
            content += '<input id="id_board_owner" name="board_owner" type="hidden" value="' + publications[i].board_owner_id + '">';
            content += '<input id="id_parent" name="parent" type="hidden">';
            content += '<div class="row">';
            content += '<div class="col s12">';
            content += '<div class="row">';
            content += '<div class="input-field col s12">';
            content += '<textarea class="materialize-textarea message-reply" id="message-reply-' + publications[i].id + '" cols="40" maxlength="500" name="content" placeholder="Responder a @' + publications[i].author_username + '" rows="10" required=""></textarea>';
            content += '<label for="message-reply-' + publications[i].id + '">Escribe tu mensaje aqui...</label>';
            content += '</div></div></div></div>';
            content += '<button type="button" id="reply-' + publications[i].id + '" class="waves-effect waves-light btn right blue enviar">Enviar<i class="material-icons right">send</i></button>';
            content += '</form></div></div>';
            if (publications[i].descendants > 0) {
                content += '<div class="row">';
                content += '<div class="col s12">';
                content += '<a class="waves-effect waves-light btn-large blue darken-1 white-text center" href="#" id="load_more_publications" data-id="' + publications[i].id + '"><i class=" material-icons left">expand_more</i>Cargar comentarios (' + publications[i].descendants + ')</a>';
                content += '<div>';
                content += '<div class="progress" id="load_publications_descendants" style="display: none;">';
                content += '<div class="indeterminate blue darken-1"></div></div>';
                content += '</div></div></div>';
            }
            content += "    </div></div></div>";
            $(content).appendTo(children_list).hide().fadeIn(250);
        }
        var child_count = $(btn).find('#child_count');
        var result_child_count = parseInt($(child_count).html(), 10) - publications.length;
        if (result_child_count > 0)
            $(child_count).html(result_child_count);
        else
            $(btn).remove();
    } else if (is_skyline) {
        for (i = 0; i < publications.length; i++) {
            pub_to_add = $('pub-' + publications[i].id);
            if (undefined !== pub_to_add && pub_to_add.length) continue;

            content = '<div class="row">';
            content += '<div class="col s12">';
            if (publications[i].level > 0 && publications[i].level < 3) {
                content += ' <div class="col s12 wrapper" id="pub-' + publications[i].id + '" data-id="' + publications[i].user_id + '" style="min-width: 98% !important;">';
            } else
                content += ' <div class=\"col s12 wrapper\" id="pub-' + publications[i].id + '" data-id="' + publications[i].user_id + '">';
            content += "            <div class=\"box\">";
            content += '            <span id="check-' + publications[i].id + '" class=\"top-options zoom-pub tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Ver conversación completa\"><i class=\"fa fa-plus-square-o\" aria-hidden=\"true\"><\/i><\/span>';
            if (publications[i].user_id == publications[i].author_id && (publications[i].event_type == 1 || publications[i].event_type == 3)) {
                content += '            <span data-id="' + publications[i].id + '" id=\"edit-comment-content\" class=\"top-options edit-comment tooltipped\" data-position=\"bottom\" data-delay=\"50\" data-tooltip=\"Editar comentario\"><i class=\"fa fa-pencil\" aria-hidden=\"true\"><\/i><\/span>';
            }
            content += '<div class="row">';
            content += "                <div class=\"articulo col s12\">";
            content += '<div class="row">';
            if (publications[i].user_id == publications[i].author_id) {
                content += '      <div class="image col l1 m2 s2" style="box-shadow: 0 1px 5px rgba(129, 199, 132, 1);">';
            } else {
                content += "      <div class=\"image col l1 m2 s2\">";
            }
            content += '        <div class="usr-img img-responsive"><img src="' + publications[i].author_avatar + '" alt="' + publications[i].author_username + '" width="120" height="120"></div>';
            content += "      </div>";
            content += '<div class="col l10 m12 s9">';
            content += '                  <h2 class="h22"><a href="/profile/' + publications[i].author_username + '" >@' + publications[i].author_username + '</a>';

            if (publications[i].parent) {
                content += '<span class="chip">';
                content += '<img src="' + publications[i].parent_avatar + '" alt="' + publications[i].parent_author + '">';
                content += '<i class="fa fa-reply"></i> <a href="/profile/' + publications[i].parent_author + '">@' + publications[i].parent_author + '</a>';
                content += '</span>';
            }
            content += '</h2>';
            content += '                    <p id="pub-created" class="blue-text text-darken-2">' + publications[i].created + '<\/p><br>';
            content += '<div class="row">';
            content += "                  <div class=\"parrafo comment\">";
            content += '                      <div class="wrp-comment">' + publications[i].content + '<\/div>';
            content += "                  </div>";
            content += '                    <div class="show-more" id="show-comment-' + publications[i].id + '">';
            content += "                        <a href=\"#\">+ Mostrar más<\/a>";
            content += "                    </div>";
            content += "                    </div>";
            if (publications[i].extra_content) {
                content += '<div class="card small">';
                content += '<div class="card-image">';
                if (publications[i].extra_content_image) {
                    content += '<img src="' + publications[i].extra_content_image + '">';
                } else {
                    content += '<img src="/static/dist/img/nuevo_back.png">';
                }
                content += '<span class="card-title white-text">' + publications[i].extra_content_title + '</span>';
                content += '</div>';
                content += '<div class="card-content">';
                content += '<p>' + publications[i].extra_content_description + '</p>';
                content += '</div>';
                content += '<div class="card-action">';
                content += '<a href="' + publications[i].extra_content_url + '">Ver</a>';
                content += '</div></div>';
            }
            if (publications[i].image) {
                                content += '<div class="row">';
                                content += '<div class="col s7">';
                                content += '<img class="responsive-img" src="'+publications[i].image+'" alt="Imagen de: '+publications[i].author_username+'" title="Imagen de: '+publications[i].author_username+'">';
            }
            if (publications[i].event_type === 6) {
                content += '<style>.comment .fa-share {color: #1e88e5;font-style: normal;}</style>';
                content += '<div class="card grey lighten-5">';
                content += '<div class="card-content black-text">';
                content += '<img src="' + publications[i].shared_pub_avatar + '" alt="' + publications[i].shared_pub_author + '" width="70" height="70" style="box-shadow: 0 1px 5px rgba(30, 136, 229, 0.15);"><br>';
                content += '<span class="card-title"><a href="/profile/' + publications[i].shared_pub_author + '">@' + publications[i].author_username + '</a>';
                content += '<i class="blue-text text-darken-2"> ' + publications[i].shared_created + '</i></span>';
                content += '<p>' + publications[i].shared_pub_content + '</p>';
                if (publications[i].shared_image) {
                    content += '<br><div class="row">';
                    content += '<div class="col s7">';
                    content += '<img class="responsive-img" src="'+publications[i].shared_image+'" alt="Imagen de: '+publications[i].shared_pub_author+'" title="Imagen de: '+ publications[i].shared_pub_author +'">';
                    content += '</div></div>';
                }
                if (publications[i].shared_pub_extra_url !== undefined && publications[i].shared_pub_extra_url) {
                    content += '<div class="card small">';
                    content += '<div class="card-image">';
                    if (publications[i].shared_pub_extra_image)
                        content += '<img src="'+publications[i].shared_pub_extra_image+'">';
                    else
                        content += '<img src="/static/dist/img/nuevo_back.png">';
                    content += '<span class="card-title white-text">'+publications[i].shared_pub_extra_title+'</span></div>';
                    content += '<div class="card-content">';
                    content += '<p>'+publications[i].shared_pub_extra_description+'</p></div>';
                    content += '<div class="card-action">';
                    content += '<a href="'+publications[i].shared_pub_extra_url+'">Ver</a></div></div></div>';

                }
                content += '<div class="card-action">';
                content += '<a class="blue-text text-darken-2" href="/publication/' + publications[i].shared_pub_id + '">Ver</a></div></div>';
            }
            content += "                    </div>";
            content += "                    </div>";
            content += "                    </div>";
            content += "                    </div>";
            content += '<div class="row">';
            content += '<div class="divider"></div>';
            content += "                <div class=\"options_comentarios\" id=\"options-comments\">";
            content += "                    <ul class=\"opciones\">";
            if (publications[i].user_id == publications[i].board_owner_id || publications[i].user_id == publications[i].author_id) {
                content += "                             <li class=\"trash-comment\" title=\"Borrar comentario\"><i class=\"fa fa-trash\"><\/i><\/li>";
            }
            if (publications[i].user_id != publications[i].author_id) {
                content += "                            <li title=\"No me gusta\" class=\"hate-comment\" id=\"fa-hate\">";
                content += '                                <i class="fa fa-angle-down" aria-hidden="true"></i>';
                content += '                                <i class="fa hate-value">'+ (publications[i].hates > 0 ? publications[i].hates : '') +'</i>';
                content += "                            </li>";
                content += '                        <li id="like-heart" title="¡Me gusta!" class="like-comment"><i class="fa fa-angle-up" aria-hidden="true"></i><i id="like-value" class="fa">'+ (publications[i].likes > 0 ? publications[i].likes : '') +'</i></li>';
            }
            content += '                       <li title="Añadir a mi skyline" data-id="'+publications[i].id+'" class="add-timeline" id="add_to_skyline"><i class="fa fa-quote-right" aria-hidden="true"> '+ (publications[i].shares > 0 ? publications[i].shares : '') +'</i></li>';
            content += '                       <li title="Responder" class="reply-comment"><i class="fa fa-reply" id="reply-caja-comentario-' + publications[i].id + '"><\/i><\/li>';
            content += "                    </ul>";
            content += "                </div>";
            content += "                </div>";
            content += "    </div>";
            if (publications[i].user_id == publications[i].author_id) {
                content += '<div data-user-id="' + publications[i].author_id + '" id="author-controls-' + publications[i].id + '" class="author-controls">';
                content += '<div class="row">';
                content += '<div class="col s12">';
                content += '<form method="post" accept-charset="utf-8">';
                content += '<input type="hidden" name="csrfmiddlewaretoken" value="' + publications[i].token + '">';
                content += '<div class="row">';
                content += '<div class="input-field col s12">';
                content += '<i class="material-icons prefix">create</i>';
                content += '<textarea class="materialize-textarea" placeholder="Escribe el contenido del nuevo mensaje" id="id_caption-' + publications[i].id + '" cols="40" maxlength="500" name="content" rows="10" required="required" style="height: 10.9969px;"></textarea>';
                content += '<label for="id_caption-' + publications[i].id + '">Editar comentario</label></div>';
                content += '<div class="row">';
                content += '<button data-id="' + publications[i].id + '" class="waves-effect waves-light btn blue darken-1 right edit-comment-btn" type="button" id="submit_edit_publication">Editar<i class="material-icons right">mode_edit</i></button>';
                content += '</div></div></form></div></div></div>';
            }
            content += '<div class="wrapper-reply">';
            content += '<div class="hidden" id="caja-comentario-' + publications[i].id + '">';
            content += '<form class="reply-form" action="" method="post">';
            content += '<input type="hidden" name="csrfmiddlewaretoken" value="' + publications[i].token + '">';
            content += '<input id="id_author" name="author" type="hidden" value="' + publications[i].user_id + '">';
            content += '<input id="id_board_owner" name="board_owner" type="hidden" value="' + publications[i].board_owner_id + '">';
            content += '<input id="id_parent" name="parent" type="hidden">';
            content += '<div class="row">';
            content += '<div class="col s12">';
            content += '<div class="row">';
            content += '<div class="input-field col s12">';
            content += '<textarea class="materialize-textarea message-reply" id="message-reply-' + publications[i].id + '" cols="40" maxlength="500" name="content" placeholder="Responder a @' + publications[i].author_username + '" rows="10" required=""></textarea>';
            content += '<label for="message-reply-' + publications[i].id + '">Escribe tu mensaje aqui...</label>';
            content += '</div></div></div></div>';
            content += '<button type="button" id="reply-' + publications[i].id + '" class="waves-effect waves-light btn right blue enviar">Enviar<i class="material-icons right">send</i></button>';
            content += '</form></div></div>';
            if (publications[i].descendants > 0) {
                content += '<div class="row">';
                content += '<div class="col s12">';
                content += '<a class="waves-effect waves-light btn-large blue darken-1 white-text center" href="#" id="load_more_publications" data-id="' + publications[i].id + '"><i class=" material-icons left">expand_more</i>Cargar comentarios (' + publications[i].descendants + ')</a>';
                content += '<div>';
                content += '<div class="progress" id="load_publications_descendants" style="display: none;">';
                content += '<div class="indeterminate blue darken-1"></div></div>';
                content += '</div></div></div>';
            }
            content += "    </div></div></div>";
            $('#tab-comentarios').find('#loader_skyline').before(content);
        }

        if (publications === undefined || publications.length <= 20)
            $(btn).remove();
        else
            $(btn).attr("data-id", publications[publications.length - 1].id);
    }
}
/* LOAD MORE COMMENTS */
function AJAX_load_publications(pub, loader, last_pub, btn) {
    var data = {
        'id': pub,
        'last_pub': last_pub,
        'csrfmiddlewaretoken': csrftoken
    };
    $.ajax({
        url: '/publication/load/more/',
        type: 'POST',
        dataType: 'json',
        data: data,

        success: function (data) {
            var response = data.response;
            if (response == true) {
                add_loaded_publication(pub, data.pubs, btn, false);
            } else {
                swal({
                    title: "Fail",
                    customClass: 'default-div',
                    text: "Failed to load more publications.",
                    type: "error"
                });
            }
        },
        complete: function () {
            $(loader).fadeOut();
        },
        error: function (rs, e) {
        }
    });
}

function AJAX_load_skyline(loader, btn) {
    if ($(btn) === undefined || !($(btn).length)) return;

    var pub = $(btn).attr("data-id");
    var data = {
        'id': pub,
        'csrfmiddlewaretoken': csrftoken
    };
    $.ajax({
        url: '/publication/load/skyline/',
        type: 'POST',
        dataType: 'json',
        data: data,

        success: function (data) {
            var response = data.response;
            if (response == true) {
                add_loaded_publication(pub, data.pubs, btn, true);
            } else {
                swal({
                    title: "Fail",
                    customClass: 'default-div',
                    text: "Failed to load more publications.",
                    type: "error"
                });
            }
        },
        complete: function () {
            $(loader).fadeOut();
        },
        error: function (rs, e) {
        }
    });
}

/* EDIT PUBLICATION */
function AJAX_edit_publication(pub, content) {
    var data = {
        'id': pub,
        'content': content,
        'csrfmiddlewaretoken': csrftoken
    };
    $.ajax({
        url: '/publication/edit/',
        type: 'POST',
        dataType: 'json',
        data: data,

        success: function (data) {
            var response = data.data;
            console.log(data.data);
            // borrar caja publicacion
            if (response == true) {
                $('#author-controls-' + pub).fadeToggle("fast");
            } else {
                swal({
                    title: "Fail",
                    customClass: 'default-div',
                    text: "Failed to edit publish.",
                    type: "error"
                });
            }
        },
        error: function (rs, e) {
        }
    });
}

/*****************************************************/
/********** AJAX para botones de comentarios *********/
/*****************************************************/

function AJAX_delete_publication(caja_publicacion) {
    var id_pub = $(caja_publicacion).attr('id').split('-')[1];  // obtengo id
    var id_user = $(caja_publicacion).attr('data-id'); // obtengo id
    var data = {
        userprofile_id: id_user,
        publication_id: id_pub,
        'csrfmiddlewaretoken': csrftoken
    };
    //event.preventDefault(); //stop submit
    $.ajax({
        url: '/publication/delete/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            // borrar caja publicacion
            if (data == true) {
                $(caja_publicacion).fadeToggle("fast");
            } else {
                swal({
                    title: "Fail",
                    customClass: 'default-div',
                    text: "Failed to delete publish.",
                    type: "error"
                });
            }
        },
        error: function (rs, e) {
            // alert('ERROR: ' + rs.responseText + ' ' + e);
        }
    });
}

/*****************************************************/
/********** AJAX para añadir me gusta a comentario ***/
/*****************************************************/

function AJAX_add_like(caja_publicacion, heart, type) {
    var id_pub;
    if (type.localeCompare("publication") == 0) {
        id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
    } else if (type.localeCompare("timeline") == 0) {
        id_pub = $(caja_publicacion).attr('data-publication'); // obtengo id
    }
    var id_user = $(caja_publicacion).attr('data-id'); // obtengo id
    var data = {
        userprofile_id: id_user,
        publication_id: id_pub,
        'csrfmiddlewaretoken': csrftoken
    };

    $.ajax({
        url: '/publication/add_like/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            var response = data.response;
            var status = data.statuslike;
            var numLikes = $(heart).find('#like-value');
            var countLikes = numLikes.text();
            if (response == true) {
                if (!countLikes || (Math.floor(countLikes) == countLikes && $.isNumeric(countLikes))) {
                    if (status == 1) {
                        $(heart).css('color', '#f06292');
                        countLikes++;
                    } else if (status == 2) {
                        $(heart).css('color', '#555');
                        countLikes--;
                    } else if (status == 3) {
                        $(heart).css('color', '#f06292');
                        var hatesObj = $(heart).prev();
                        var hates = hatesObj.find(".hate-value");
                        var countHates = hates.text();
                        countHates--;
                        if (countHates <= 0) {
                            hates.text('');
                        } else
                            hates.text(countHates);
                        $(hatesObj).css('color', '#555');
                        countLikes++;
                    }
                    if (countLikes <= 0) {
                        numLikes.text('');
                    } else {
                        numLikes.text(countLikes);
                    }
                } else {
                    if (status == 1)
                        $(heart).css('color', '#f06292');
                    if (status == 2)
                        $(heart).css('color', '#555');
                }
            } else {
                swal({
                    title: ":-(",
                    text: "¡No puedes dar me gusta a este comentario!",
                    timer: 4000,
                    customClass: 'default-div',
                    animation: "slide-from-bottom",
                    showConfirmButton: false,
                    type: "error"
                });
            }
        },
        error: function (rs, e) {
            // alert('ERROR: ' + rs.responseText + e);
        }
    });
}

/*****************************************************/
/******* AJAX para añadir no me gusta a comentario ***/
/*****************************************************/

function AJAX_add_hate(caja_publicacion, heart, type) {
    var id_pub;
    if (type.localeCompare("publication") == 0) {
        id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
    } else if (type.localeCompare("timeline") == 0) {
        id_pub = $(caja_publicacion).attr('data-publication'); // obtengo id
    }
    var id_user = $(caja_publicacion).attr('id'); // obtengo id
    var data = {
        userprofile_id: id_user,
        publication_id: id_pub,
        'csrfmiddlewaretoken': csrftoken
    };
    //event.preventDefault(); //stop submit
    $.ajax({
        url: '/publication/add_hate/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            var statusOk = 1;
            var statusNo = 2;
            var statusInLike = 3;
            var response = data.response;
            var status = data.statuslike;
            var numHates = $(heart).find(".hate-value");
            var countHates = numHates.text();
            if (response == true) {
                if (!countHates || (Math.floor(countHates) == countHates && $.isNumeric(countHates))) {
                    if (status === statusOk) {
                        $(heart).css('color', '#ba68c8');
                        countHates++;
                    } else if (status === statusNo) {
                        $(heart).css('color', '#555');
                        countHates--;
                    } else if (status === statusInLike) {
                        $(heart).css('color', '#ba68c8');
                        countHates++;
                        var likesObj = $(heart).next();
                        var likes = likesObj.find("#like-value");
                        var countLikes = likes.text();
                        countLikes--;
                        if (countLikes <= 0) {
                            likes.text('');
                        } else
                            likes.text(countLikes);
                        $(likesObj).css('color', '#555');
                    }
                    if (countHates <= 0) {
                        numHates.text("");
                    } else {
                        numHates.text(countHates);
                    }
                } else {
                    if (status === statusOk) {
                        $(heart).css('color', '#ba68c8');
                    } else if (status === statusNo) {
                        $(heart).css('color', '#555');
                    }
                }
            } else {
                swal({
                    title: ":-(",
                    text: "¡No puedes dar no me gusta a este comentario!",
                    timer: 4000,
                    customClass: 'default-div',
                    animation: "slide-from-bottom",
                    showConfirmButton: false,
                    type: "error"
                });
            }
        },
        error: function (rs, e) {
            // alert('ERROR: ' + rs.responseText + e);
        }
    });
}

/*****************************************************/
/********** AJAX para agregar al TIMELINE *********/
/*****************************************************/
function AJAX_add_timeline(pub_id, tag, data_pub) {

    var data = {
        'publication_id': pub_id,
        'content': data_pub,
        'csrfmiddlewaretoken': csrftoken
    };

    var shared_tag = $(tag).find('.fa-quote-right');
    var count_shared = $(shared_tag).text();
    count_shared = count_shared.replace(/ /g, '');

    $.ajax({
        url: '/publication/share/publication/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            var response = data.response;
            if (response == true) {
                var status = data.status;
                if (status == 1) {
                    if (!count_shared || (Math.floor(count_shared) == count_shared && $.isNumeric(count_shared))) {
                        count_shared++;
                        if (count_shared > 0) {
                            $(shared_tag).text(" " + count_shared)
                        } else {
                            $(shared_tag).text(" ");
                        }
                    }
                    $(tag).attr("id", "remove_from_skyline");
                    $(tag).css('color', '#bbdefb');
                    $('#share-publication-wrapper').hide();
                } else if (status == 2) {
                    if (!count_shared || (Math.floor(count_shared) == count_shared && $.isNumeric(count_shared))) {
                        count_shared--;
                        if (count_shared > 0) {
                            $(shared_tag).text(" " + count_shared)
                        } else {
                            $(shared_tag).text(" ");
                        }
                    }
                    $(tag).attr("id", "add_to_skyline");
                    $(tag).css('color', '#555');
                }
            } else {
                swal({
                    title: "Fail",
                    customClass: 'default-div',
                    text: "Failed to add to timeline.",
                    type: "error"
                });
            }
        },
        error: function (rs, e) {
            // alert('ERROR: ' + rs.responseText + e);
        }
    });
}

/***** AJAX PARA BLOQUEAR USUARIO *****/
function AJAX_bloq_user(buttonBan) {
    var id_user = $("#profileId").html();
    $.ajax({
        type: 'POST',
        url: '/bloq_user/',
        data: {
            'id_user': id_user,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (data) {
            if (data.response == true) {
                $(buttonBan).css('color', '#FF6347');
                if (data.status == "none" || data.status == "isfollow") {
                    $('#addfriend').replaceWith('<span class="fa fa-ban" id="bloq-user-span" title="Bloqueado" onclick="AJAX_remove_bloq();">' + ' ' + '</span>');
                } else if (data.status == "inprogress") {
                    $('#follow_request').replaceWith('<span class="fa fa-ban" id="bloq-user-span" title="Bloqueado" onclick="AJAX_remove_bloq();">' + ' ' + '</span>');
                }
                if (data.haslike == "liked") {
                    $("#ilike_profile").css('color', '#46494c');
                    var obj_likes = document.getElementById('likes');
                    if ($(obj_likes).find("strong").html() > 0) {
                        $(obj_likes).find("strong").html(parseInt($(obj_likes).find("strong").html()) - 1);
                    }
                }
            } else {
                swal({
                    title: "Tenemos un problema...",
                    customClass: 'default-div',
                    text: "Hubo un problema con su petición.",
                    timer: 4000,
                    showConfirmButton: true
                });
            }
        }, error: function (rs, e) {
            // alert(rs.responseText + " " + e);
        }
    });
}

function AJAX_remove_bloq() {
    $.ajax({
        type: 'POST',
        url: '/remove_blocked/',
        data: {
            'slug': $("#profileId").html(),
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (response) {
            if (response == true) {
                $('#bloq-user-span').replaceWith('<span id="addfriend" class="fa fa-plus" title="Seguir" style="color:#555 !important;" onclick=AJAX_requestfriend("noabort");>' + ' ' + '</span>');
                $('#bloq-user').css('color', '#555');
            } else {
                swal({
                    title: "Tenemos un problema...",
                    customClass: 'default-div',
                    text: "Hubo un problema con su petición.",
                    timer: 4000,
                    showConfirmButton: true
                });
            }
        }, error: function (rs, e) {
            // alert(rs.responseText + " " + e);
        }
    });
}

