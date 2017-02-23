var countFriendList = 1;
var flag_reply = false;
var max_height_comment = 60;

$(document).ready(function () {
    var tab_comentarios = $('#tab-comentarios');
    var tab_timeline = $('#tab-timeline');
    var tab_amigos = $('#tab-amigos');
    var wrapper_timeline = $(tab_timeline).find('#wrapperx-timeline');

    /* Show more - Show less */
    $(tab_comentarios).find('.wrapper').each(function () {
        var comment = $(this).find('.wrp-comment');
        var show = $(this).find('.show-more a');

        if ($(comment).height() > max_height_comment) {
            $(comment).css('height', '2.6em');

        } else {
            $(show).css('display', 'none');
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
    $('#div-separator').on('click', '#options-comments .fa-reply', function () {
        var id_ = $(this).attr("id").slice(6);
        if (flag_reply) {
            $("#" + id_).slideUp("fast");
            flag_reply = false
        } else {
            $("#" + id_).slideDown("fast");
            flag_reply = true
        }
    });

    function replyComment(caja_pub) {
        var id_comment = $(caja_pub).attr('id').split('-')[1];
        var commentReply = document.getElementById('actual-' + id_comment);
        $(commentReply).toggleClass("reply-actual-message-show");
    }

    /* Expandir comentario */

    $('.fa-expand').on('click', function () {
        var caja_pub = $(this).closest('.wrapper');
        expandComment(caja_pub);
    });

    function expandComment(caja_pub) {
        var id_pub = $(caja_pub).attr('id').split('-')[1];  // obtengo id
        var commentToExpand = document.getElementById('expand-' + id_pub);
        $(commentToExpand).fadeToggle("fast");
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
        //alert($(caja_comentario).html());
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

    /* Borrar timeline */

    $(tab_timeline).find('.controles .fa-trash').on('click', function () {
        var div_timeline = $(this).closest('.timeline-pub');
        swal({
            title: "Are you sure?",
            text: "You will not be able to recover this history!",
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
                AJAX_delete_timeline(div_timeline);
            }
        });
    });


    /* Agregar timeline */
    $(document).on('click', '#options-comments .fa-tag', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var tag = this;
        AJAX_add_timeline(caja_publicacion, tag, "publication");
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

    /* Añadir publicacion de timeline a mi timeline */
    $(wrapper_timeline).find('#controls-timeline').find('#add-timeline').on('click', function () {
        var caja_publicacion = $(this).closest('.timeline-pub');
        var tag = this;
        AJAX_add_timeline(caja_publicacion, tag, "timeline");
    });
    /* Añadir me gusta a comentario en timeline */
    $(wrapper_timeline).find('#controls-timeline').find('#like-heart-timeline').on('click', function () {
        var caja_publicacion = $(this).closest('.timeline-pub');
        var heart = this;
        AJAX_add_like(caja_publicacion, heart, "timeline");
    });
    /* Añadir no me gusta a comentario en timeline */
    $(wrapper_timeline).find('#controls-timeline').find('#fa-hate-timeline').on('click', function () {
        var caja_publicacion = $(this).closest('.timeline-pub');
        var heart = this;
        AJAX_add_hate(caja_publicacion, heart, "timeline");
    });


    /* FUNCIONES AJAX PARA TABS DE PERFIL */

    $(tab_amigos).bind('scroll', function () {
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
    });


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

}); // END DOCUMENT READY */

function addFriendToHtmlList(item) {

    if (item.user__profile__image) {
        $(tab_amigos).find("ul.list").append('<li id="friend-' + item.user__id + '"><img src="' + MEDIA_URL + item.user__profile__image + '"  class="friend-avatar img-responsive"><a href="/profile/' + item.user__username + '">' + item.user__first_name + ' ' + item.user__last_name + ' (' + item.user__username + ')</a></li>');

        //SI NO EXISTE LA URL DE LA IMAGEN, SE CAMBIA POR EL AVATAR POR DEFECTO. QUITAR ESTO CUANDO
        //SE PUEDAN SUBIR IMAGENES SIN QUE DESAPAREZCAN MAS TARDE
        imageselector = $(tab_amigos).find("ul.list #friend-" + item.user__id + " img.friend-avatar")
        URL_CHECK = MEDIA_URL + item.user__profile__image;
        URL_CHANGE = STATIC_URL + 'img/default.png';
        //Check image URL;
        (function (imageselector, URL_CHECK, URL_CHANGE) {

            $.ajax({
                url: URL_CHECK,
                type: 'HEAD',
                data: {
                    'csrfmiddlewaretoken': csrftoken
                },
                dataType: "json",
                error: function () {
                    //url not exists
                    //wait secs

                    setTimeout(function () {

                        //forma chula
                        imageselector.fadeOut("slow", function () {
                            imageselector.attr("src", URL_CHANGE);
                        });
                        imageselector.fadeIn("slow");

                    }, 750);

                }

            });

        })(imageselector, URL_CHECK, URL_CHANGE);

    } else {
        $(tab_amigos).find("ul.list").append('<li id="friend-' + item.user__id + '"><img src="' + STATIC_URL + 'img/generic-avatar.png" class="friend-avatar img-responsive"><a href="/profile/' + item.user__username + '">' + item.user__first_name + ' ' + item.user__last_name + ' (' + item.user__username + ')</a></li>');
    }


}

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


function addItemToFriendList(name, lastname) {
    $("#tab-amigos").find("ul").append('<li><img src="{{STATIC_URL}}img/generic-avatar.png" class="img-responsive"><a>' + name + ' ' + lastname + '</a></li>');
}


/*****************************************************/
/********** AJAX para botones de comentarios *********/
/*****************************************************/

function AJAX_delete_publication(caja_publicacion) {
    var id_pub = $(caja_publicacion).attr('id').split('-')[1];  // obtengo id
    var id_user = $(caja_publicacion).data('id'); // obtengo id
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
        id_pub = $(caja_publicacion).data('publication'); // obtengo id
    }
    var id_user = $(caja_publicacion).data('id'); // obtengo id
    var data = {
        userprofile_id: id_user,
        publication_id: id_pub,
        'csrfmiddlewaretoken': csrftoken
    };
    //event.preventDefault(); //stop submit
    $.ajax({
        url: '/publication/add_like/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            var response = data.response;
            var status = data.statuslike;
            var numLikes = heart;
            var countLikes = numLikes.innerHTML;
            if (response == true) {
                $(heart).css('color', '#f06292');
                if (status == 1) {
                    countLikes++;
                } else if (status == 2) {
                    $(heart).css('color', '#555');
                    countLikes--;
                }
                if (countLikes == 0) {
                    numLikes.innerHTML = " ";
                } else {
                    numLikes.innerHTML = " " + countLikes;
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
        id_pub = $(caja_publicacion).data('publication'); // obtengo id
    }
    var id_user = $(caja_publicacion).data('id'); // obtengo id
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
            var response = data.response;
            var status = data.statuslike;
            var numLikes = $(heart).find(".hate-value");
            var countLikes = numLikes.text();
            if (response == true) {
                if (status == statusOk) {
                    $(heart).css('color', '#ba68c8');
                    countLikes++;
                } else if (status == statusNo) {
                    $(heart).css('color', '#555');
                    countLikes--;
                }
                if (countLikes == 0) {
                    numLikes.text(" ");
                } else {
                    numLikes.text(countLikes);
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

function AJAX_add_timeline(caja_publicacion, tag, type) {
    var id_pub;
    if (type.localeCompare("publication") == 0) {
        id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
    } else if (type.localeCompare("timeline") == 0) {
        id_pub = $(caja_publicacion).data('publication'); // obtengo id
    }
    var id_user = $(caja_publicacion).data('id'); // obtengo id
    var data = {
        userprofile_id: id_user,
        publication_id: id_pub,
        'csrfmiddlewaretoken': csrftoken
    };
    //event.preventDefault(); //stop submit
    $.ajax({
        url: '/timeline/add_to_timeline/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            // borrar caja publicacion
            if (data == true) {
                $(tag).css('color', '#bbdefb');
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
/*****************************************************/
/********** AJAX para borrado de timeline ***********/
/****************************************************/

function AJAX_delete_timeline(div_timeline) {
    var id_pub = $(div_timeline).attr('id').split('-')[1];  // obtengo id
    var id_user = $(div_timeline).data('id'); // obtengo id
    var data = {
        userprofile_id: id_user,
        timeline_id: id_pub,
        'csrfmiddlewaretoken': csrftoken
    };
    //alert("id pub: " + id_pub + " id_user: " + id_user);
    //event.preventDefault(); //stop submit
    $.ajax({
        url: '/timeline/remove_timeline/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            // borrar caja timeline
            if (data == true) {
                $(div_timeline).fadeToggle("fast");
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
            // alert('ERROR: ' + rs.responseText + " " + e);
        }
    });
}
