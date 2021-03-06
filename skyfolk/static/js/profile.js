var countFriendList = 1;
var flag_reply = false;
var max_height_comment = 60;

var cheat = document.getElementById('atajos-keyboard-profile');

$(document).ready(function () {
    var tab_comentarios = $('#tab-comentarios');
    var tab_amigos = $('#tab-amigos');
    var wrapper_shared_pub = $('#share-publication-wrapper');
    // var add_pin = $('.add-plugin');

    // $(add_pin).hide();

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

    $('.menu-profile').on('click', function () {
        $(".info-paw").show();
    });

    $('.info-trof').on('click', function () {
        var id = $(this).data('id');
        $(".trofeos").toggle(0, function () {
            if ($(this).is(":visible")) {
                $('.wrapper-trofeos').load('/awards/user/' + id + '/');
            }
        });
    });

    $('.info-groups').on('click', function () {
        var id = $(this).data('id');
        $(".grupos").toggle(0, function () {
            if ($(this).is(":visible")) {
                $('.wrapper-groups').load('/groups/profile/' + id + '/');
            }
        });
    });


    $('.info-workspaces').on('click', function () {
        var id = $(this).data('id');
        $(".workspaces").toggle(0, function () {
            if ($(this).is(":visible")) {
                $('.wrapper-workspaces').load('/dashboard/public/workspaces/' + id + '/');
            }
        });
    });

    $('#close-workspaces').on('click', function () {
        $(".workspaces").hide();
    });

    $('#close-trofeos').on('click', function () {
        $(".trofeos").hide();
    });

    $('#close-grupos').on('click', function () {
        $(".grupos").hide();
    });

    $('.trofeos').on('click', '.next-awards, .prev-awards', function (e) {
        e.preventDefault()
        $('.wrapper-trofeos').load($(this).attr('href'));
    });

    $('.grupos').on('click', '.wrapper-groups .pagination a', function (e) {
        e.preventDefault()
        $('.wrapper-groups').load($(this).attr('href'));
    });

    $('.workspaces').on('click', '.wrapper-workspaces .pagination a', function (e) {
        e.preventDefault()
        $('.wrapper-workspaces').load($(this).attr('href'));
    });

    $('#configurationOnProfile').on('click', function () {
        var configIcon = $(this).find('.configure-profile');

        $(configIcon).text(function (i, oldText) {
            if (oldText === 'settings') {
                return 'remove_red_eye';
            }
            if (oldText === 'remove_red_eye') {
                return 'settings';
            }
        });

        $('html, body').toggleClass('body-inConf');
        $('.ventana-pin').fadeToggle();
        $('.add-plugin').toggleClass('hide');
    });

    /* Abrir respuesta a comentario */
    $(tab_comentarios).on('click', '.options_comentarios .reply-comment', function () {
        var id_ = $(this).attr("id").slice(6);
        $("#" + id_).slideToggle("fast");
    });

    /* Editar comentario */
    $(tab_comentarios).on('click', '.edit-comment', function () {
        Materialize.updateTextFields();
        var id = $(this).attr('data-id');
        $("#author-controls-" + id).slideToggle("fast");
    });

    $(tab_comentarios).on('click', '.edit-comment-btn', function (event) {
        event.preventDefault();
        var edit = $(this).closest('form').serialize();
        edit += '&csrfmiddlewaretoken=' + csrftoken;
        AJAX_edit_publication(edit);
    });

    function replyComment(caja_pub) {
        var id_comment = $(caja_pub).attr('id').split('-')[1];
        var commentReply = document.getElementById('actual-' + id_comment);
        $(commentReply).toggleClass("reply-actual-message-show");
    }

    /* Bloquear usuario on key press */
    $(this).keypress(function (e) {
        var key = e.keyCode || e.which;
        if (key === 66 && !($('input').is(":focus")) && !($('textarea').is(":focus"))) {
            AJAX_bloq_user($('#bloq-user'));
        }
    });

    /* Dar like on key press */
    $(this).keypress(function (e) {
        var key = e.keyCode || e.which;
        if (key === 70 && !($('input').is(":focus")) && !($('textarea').is(":focus"))) {
            AJAX_likeprofile("noabort");
        }
    });
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
    $(tab_comentarios).on('click', '.options_comentarios .trash-comment', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        swal({
            title: "¿Estás seguro?",
            text: "¡No podrás recuperar esta publicación!",
            type: "warning",
            animation: "slide-from-top",
            showConfirmButton: true,
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Sí",
            cancelButtonText: "¡No!",
            closeOnConfirm: true
        }, function (isConfirm) {
            if (isConfirm) {
                AJAX_delete_publication(caja_publicacion);
            }
        });
    });

    /* Agregar skyline */
    $(this).on('click', '.add-timeline', function (e) {
        var tag = $(this);
        $(wrapper_shared_pub).find('#id_pk').val($(tag).data('id'));
        $(wrapper_shared_pub).show();
        $("html, body").animate({scrollTop: 0}, "slow");
    });

    /* Compartir a skyline */
    $(wrapper_shared_pub).find('#share_publication_form').on('submit', function (event) {
        event.preventDefault();
        var content = $(this).serialize();
        content += '&csrfmiddlewaretoken=' + csrftoken;
        var pub_id = $(wrapper_shared_pub).find('#id_pk').val();
        var tag = $('#pub-' + pub_id).find('.add-timeline').first();
        AJAX_add_timeline(pub_id, tag, content);
    });

    /* Cerrar div de compartir publicacion */
    $('#close_share_publication').click(function () {
        $(wrapper_shared_pub).hide();
        $(wrapper_shared_pub).find('#id_pk').val('');
    });

    /* Eliminar skyline */
    $(this).on('click', '.remove-timeline', function () {
        var tag = $(this);
        AJAX_remove_timeline(tag.data('id'), tag);
    });

    /* Añadir me gusta a comentario */
    $(document).on('click', '.like-comment', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        AJAX_add_like(caja_publicacion, heart, "publication");
    });

    /* Añadir no me gusta a comentario */
    $(document).on('click', '.hate-comment', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = $(this);
        AJAX_add_hate(caja_publicacion, heart, "publication");
    });

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

    $('.profile-controls').on('click', '#bloq-user', function () {
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

    /* LOAD MORE ON CLICK */
    $(tab_comentarios).on('click', '.load_more_publications', function (e) {
        e.preventDefault();
        var loader = $(this).next().find('.load_publications_descendants');
        var pub_id = $(this).data('id');
        var page = $('.page_for_' + pub_id).last().val();
        if (typeof page === 'undefined') {
            page = 1;
        }
        AJAX_load_publications(pub_id, loader, page, this);
    });

    $(tab_amigos).on('click', '.infinite-more-followed', function (e) {
        e.preventDefault();
        var _next = $(this).attr('href');
        $.get(_next, function (data, status) {
            var $load_following = $('.load_following');
            $load_following.show();
            var _items = $(data).find('.item-followed');
            $('.infinite-following').append(_items);
            $('.infinite-more-followed').replaceWith($(data).find('.infinite-more-followed'));
            $load_following.hide();
        }).always(function () {

        });
    });

    $('.widget-controls').on('click', '.update-plugin', function (e) {
        e.preventDefault();
        var plugin_uid = $(this).data('id');
        AJAX_update_entry_info(plugin_uid);
    });

    $('.interests').mouseenter(function () {
        var interests = $(this);
        var username = interests.attr('data-username');
        $.get("/profile/" + username + "/interests/", function (data) {
            interests.attr('data-tooltip', data.join());
        });
    });
}); // END DOCUMENT READY */

/*PETICION AJAX PARA 'I LIKE' DEL PERFIL*/
function AJAX_likeprofile(status) {
    if (status === "noabort") $.ajax({
        type: "POST",
        url: "/like_profile/",
        data: {
            'slug': $("#profileId").html(),
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (response) {
            var _likes = $('#likes').find('.likes-number');
            if (response === "like") {
                $("#ilike_profile").css('color', '#ec407a');
                $(_likes).html(parseInt($(_likes).html()) + 1);
            } else if (response === "nolike") {
                $("#ilike_profile").css('color', '#46494c');
                if ($(_likes).html() > 0) {
                    $(_likes).html(parseInt($(_likes).html()) - 1);
                }
            } else if (response === "blocked") {
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
    }); else if (status === "anonymous") {
        swal({
            title: "¡Ups!",
            text: "Debe estar registrado",
            customClass: 'default-div'
        });
    }

}

/* LOAD MORE COMMENTS */
function AJAX_load_publications(pub, loader, page, btn) {
    $.ajax({
        url: '/publication/load/more/?pubid=' + pub + '&page=' + page,
        type: 'GET',
        beforeSend: function () {
            $(loader).fadeIn();
        },
        success: function (data) {
            var $existing = $('#list-publications').find('#pub-' + pub).first();
            var $children_list = $existing.find('.children').first();

            $(data).find('[id^="pub-"]').each(function () {
                var pub_id = $(this).attr('id');
                var element = $('#' + pub_id);
                if (element.length) {
                    element.remove();
                }
            });

            $children_list.append(data);
            var $child_count = $(btn).find('.child_count');
            var $result_child_count = parseInt($child_count.html(), 10) - $('.childs_for_' + pub).last().val();
            if ($result_child_count > 0) {
                $($child_count).html($result_child_count);
            } else {
                $(btn).remove();
            }
        },
        complete: function () {
            $(loader).fadeOut();
            $('.dropdown-button').dropdown();
        },
        error: function (rs, e) {
            console.log(e);
        }
    });
}

/* EDIT PUBLICATION */
function AJAX_edit_publication(data) {
    $.ajax({
        url: '/publication/edit/',
        type: 'POST',
        dataType: 'json',
        data: data,

        success: function (data) {
            var response = data.data;
            // borrar caja publicacion
            if (response === false) {
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
            if (data.response == true) {
                $(caja_publicacion).fadeToggle("fast");
                if (data.shared_pub_id) {
                    var shared_btn = $('#share-' + data.shared_pub_id);
                    var shared_btn_child = shared_btn.find('.share-values');
                    var countShares = $(shared_btn_child).text();
                    if (!countShares || (Math.floor(countShares) == countShares && $.isNumeric(countShares))) {
                        countShares--;
                        countShares > 0 ? shared_btn_child(countShares) : shared_btn_child.text('');
                    }
                    shared_btn.attr('class', 'add-timeline');
                    shared_btn.css('color', '#555');
                }
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
            var numLikes = $(heart).closest('.score-controls').find('.score-comment');
            var countLikes = numLikes.text();
            if (response === true) {
                if (!countLikes || (Math.floor(countLikes) == countLikes && $.isNumeric(countLikes))) {
                    countLikes = parseInt(countLikes);
                    if (status === 1) {
                        countLikes++;
                    } else if (status === 2) {
                        countLikes--;
                    } else if (status === 3) {
                        countLikes = countLikes + 2;
                    }
                    numLikes.text(countLikes);
                }
                if (status === 1) {
                    $(heart).css('border-bottom', "20px solid #66bb6a");
                } else if (status === 2) {
                    $(heart).css('border-bottom', "20px solid");
                } else if (status === 3) {
                    let hateObj = $(heart).closest('.score-controls').find('.hate-comment');
                    $(heart).css('border-bottom', "20px solid #66bb6a");
                    $(hateObj).css('border-top', "20px solid");
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
            var numHates = $(heart).closest('.score-controls').find('.score-comment');
            var countHates = numHates.text();
            if (response === true) {
                if (!countHates || (Math.floor(countHates) == countHates && $.isNumeric(countHates))) {
                    countHates = parseInt(countHates);
                    if (status === statusOk) {
                        countHates--;
                    } else if (status === statusNo) {
                        countHates++;
                    } else if (status === statusInLike) {
                        countHates = countHates - 2;
                    }
                    numHates.text(countHates);
                }
                if (status === statusOk) {
                    $(heart).css('border-top', "20px solid #ef5350");
                } else if (status === statusNo) {
                    $(heart).css('border-top', "20px solid");
                } else if (status === statusInLike) {
                    let likesObj = $(heart).closest('.score-controls').find('.like-comment');
                    $(heart).css('border-top', "20px solid #ef5350");
                    $(likesObj).css('border-bottom', "20px solid");
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

    var shared_tag = $(tag).find('.share-values');
    var count_shared = $(shared_tag).text();
    count_shared = count_shared.replace(/ /g, '');

    $.ajax({
        url: '/publication/share/publication/',
        type: 'POST',
        dataType: 'json',
        data: data_pub,
        success: function (data) {
            if (data === true) {
                if (!count_shared || (Math.floor(count_shared) == count_shared && $.isNumeric(count_shared))) {
                    count_shared++;
                    if (count_shared > 0) {
                        $(shared_tag).text(" " + count_shared);
                    } else {
                        $(shared_tag).text(" ");
                    }
                }
                $(tag).attr("class", "remove-timeline");
                $(tag).css('color', '#bbdefb');
                $('#share-publication-wrapper').hide();
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

function AJAX_remove_timeline(pub_id, tag) {
    var shared_tag = $(tag).find('.share-values');
    var count_shared = $(shared_tag).text();
    count_shared = count_shared.replace(/ /g, '');

    $.ajax({
        url: '/publication/delete/share/publication/',
        type: 'POST',
        dataType: 'json',
        data: {
            'pk': pub_id
        },
        success: function (data) {
            var response = data.response;
            if (response === true) {
                if (!count_shared || (Math.floor(count_shared) == count_shared && $.isNumeric(count_shared))) {
                    count_shared--;
                    if (count_shared > 0) {
                        $(shared_tag).text(" " + count_shared);
                    } else {
                        $(shared_tag).text(" ");
                    }
                }
                $(tag).attr("class", "add-timeline");
                $(tag).css('color', '#555');
                $('#pub-' + data.id_to_delete).remove();

            } else {
                swal({
                    title: "Fail",
                    customClass: 'default-div',
                    text: "Failed to add to timeline.",
                    type: "error"
                });
            }
        },
        error: function (jqXHR, textStatus, errorThrown) {
            // console.log(jqXHR.status);
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
                if (data.status === "none" || data.status === "isfollow") {
                    $('#addfriend').replaceWith('<li class="material-icons block-profile" id="bloq-user-span" title="Bloqueado" onclick="AJAX_remove_bloq();">' + 'block' + '</li>');
                    $(buttonBan).remove();
                } else if (data.status === "inprogress") {
                    $('#follow_request').replaceWith('<li class="material-icons block-profile" id="bloq-user-span" title="Bloqueado" onclick="AJAX_remove_bloq();">' + 'block' + '</li>');
                    $(buttonBan).remove();
                }
                if (data.haslike === "liked") {
                    $("#ilike_profile").css('color', '#46494c');
                    var obj_likes = document.getElementById('likes');
                    if ($(obj_likes).find(".likes-number").html() > 0) {
                        $(obj_likes).find(".likes-number").html(parseInt($(obj_likes).find(".likes-number").html()) - 1);
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
                $('#bloq-user-span').replaceWith('<li id="addfriend" class="material-icons follow-profile" title="Seguir" style="color:#555 !important;" onclick=AJAX_requestfriend("noabort");>' + 'add' + '</li>');
                $('.profile-controls').append('<li id="bloq-user"><i class="material-icons" aria-hidden="true">block</i></li>');
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

function AJAX_update_entry_info(plugin_uid) {
    $.ajax({
        type: 'POST',
        url: '/dashboard/entry/update/',
        data: {
            'plugin_uid': plugin_uid,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (data) {
            alert(data.plugin_uid);
        }, error: function (rs, e) {
            alert('ERROR');
        }
    })
}