$(function () {
    var _group_profile = $('#group-profile');
    var $tab_commentarios = $('#tab-comentarios');

    $("#li-tab-amigos").click(function () {
        $('#tab-amigos').css({
            "overflow": "auto"
        });
    });

    $("#li-tab-comentarios").click(function () {
        $('#tab-comentarios').css({
            "overflow": "auto"
        });

    });

    $("#li-tab-timeline").click(function () {
        $('#tab-timeline').css({
            "overflow": "auto"
        });
    });

    $("#publish_group").click(function (e) {
        if (!$('#group_form_wrapper').is(':visible')) {
            $('#group_form_wrapper').show();
        } else {
            $('#group_form_wrapper').hide();
        }
    });
    $('#group_form_wrapper .close').click(function () {
        $('#group_form_wrapper').hide();
    });

    /* Submit publication */
    $('#group_form_wrapper').find('#group_publication').on('submit', function (event) {
        event.preventDefault();
        var form = $(this);
        AJAX_submit_group_publication(form, 'publication');
    });
    $(_group_profile).on('click', '#cancel_group_request', function () {
        AJAX_remove_group_request();
        return false;
    });
    // FOLLOW GROUP
    $(_group_profile).on('click', '#follow-group', function (e) {
        e.preventDefault();
        var id = $(_group_profile).attr('data-id');
        AJAX_follow_group(id);
        return false;
    });
    // UNFOLLOW GROUP
    $(_group_profile).on('click', '#unfollow-group', function (e) {
        e.preventDefault();
        var id = $(_group_profile).attr('data-id');
        AJAX_unfollow_group(id);
        return false;
    });

    // LIKE GROUP
    $(_group_profile).on('click', '#like-group', function (e) {
        e.preventDefault();
        var id = $(_group_profile).attr('data-id');
        AJAX_like_group(id);
        return false;
    });
    // KICK MEMBER
    $('.kick-member').click(function () {
        var id = $(this).data('id');
        var group_id = $('#group_id').val();
        swal({
            title: "¿Estas seguro?",
            text: "¡Vas a expulsar a este miembro del grupo!",
            type: "warning",
            animation: "slide-from-top",
            showConfirmButton: true,
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Si, estoy seguro",
            cancelButtonText: "¡No!",
            closeOnConfirm: false,
        }, function (isConfirm) {
            if (isConfirm) {
                AJAX_kick_member(id, group_id);
            }
        });
    });
    /* Borrar publicacion */
    $tab_commentarios.on('click', '.trash-comment', function () {
        var id = $(this).closest('.options_comentarios').data('id');
        var board_group = $(this).closest('.options_comentarios').data('board');
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
                AJAX_delete_group_publication(id, board_group);
            }
        });
    });

    /* Responder comentario */
    /* Abrir respuesta a comentario */
    $tab_commentarios.on('click', '.reply-comment', function () {
        var id_ = $(this).attr("id").slice(6);
        $("#" + id_).slideToggle("fast");
    });
    /* Submit reply publication */
    $tab_commentarios.on('click', '.group_reply', function (event) {
        event.preventDefault();
        var form = $(this).closest('form');
        var parent_pk = $(this).attr('id').split('-')[1];
        AJAX_submit_group_publication(form, 'reply', parent_pk);
    });

    /* ADD LIKE */
    $tab_commentarios.on('click', '.like-comment', function () {
        var pub_box = $(this).closest('.wrapper').closest('.row');
        AJAX_add_like_group_publication(pub_box, $(this), "publication");
    });
    /* ADD HATE */
    $('#tab-comentarios').on('click', '.hate-comment', function () {
        var pub_box = $(this).closest('.wrapper').closest('.row');
        AJAX_add_hate_group_publication(pub_box, $(this), "publication");
    });
    /* EDIT COMMENT */

    $tab_commentarios.on('click', '.edit-comment', function () {
        var id = $(this).attr('data-id');
        $("#author-controls-" + id).slideToggle("fast");
    });

    $tab_commentarios.on('click', '.edit-comment-btn', function (event) {
        event.preventDefault();
        var id = $(this).attr('data-id');
        var content = $(this).closest('#author-controls-' + id).find('#id_caption-' + id).val();
        AJAX_edit_group_publication(id, content);
    });

    $tab_commentarios.on('click', '.zoom-pub', function () {
        window.location.href = $(this).data('url');
    });

    $tab_commentarios.on('click', '.load_more_publications', function (e) {
        e.preventDefault();
        var loader = $(this).next().find('.load_publications_descendants');
        var pub_id = $(this).data('id');
        var page = $(this).attr('href');
        AJAX_load_descendants_group(pub_id, loader, page, $(this));
    });
});// end document ready

var loadDescendantsRunning = false;

function AJAX_follow_group(_id) {
    $.ajax({
        type: 'POST',
        url: '/follow_group/',
        data: {
            'id': _id,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (response) {
            var _response = response.response;
            if (_response === "user_add") {
                $('#follow-group').text('remove');
                $('#follow-group').attr({
                    "id": "unfollow-group",
                    "class": "material-icons group-follow",
                    "style": "color: #29b203;"
                });

            } else if (_response === "own_group") {
                swal({
                    title: "¡Ups!",
                    text: "¡No puedes seguir a tu propio grupo!",
                    customClass: 'default-div'
                });
            } else if (_response === "in_progress") {
                $('#follow-group').replaceWith('<span class="cancel-request material-icons" id="cancel_group_request" title="En proceso">' + 'watch_later' + '</span>');
            } else {
                swal({
                    title: "¡Ups!",
                    text: "Hay un error con tu petición, intentalo de nuevo mas tarde.",
                    customClass: 'default-div'
                });
            }
        },
        error: function (rs, e) {

        }
    });
}

function AJAX_unfollow_group(_id) {
    $.ajax({
        type: 'POST',
        url: '/unfollow_group/',
        data: {
            'id': _id,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (response) {
            if (response == "user_unfollow") {
                $('#unfollow-group').text('add');
                $('#unfollow-group').attr({
                    "id": "follow-group",
                    "class": "material-icons group-follow",
                    "style": "color: #555;"
                });
            } else if (response == false) {
                swal({
                    title: "¡Ups!",
                    text: "Hay un error con tu petición, intentalo de nuevo mas tarde.",
                    customClass: 'default-div'
                });
            }
        }, error: function (rs, e) {
            // swal(rs.responseText + " " + e);
        }
    });
}

function AJAX_like_group(_id) {
    $.ajax({
        type: 'POST',
        url: '/like_group/',
        data: {
            'id': _id,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (response) {
            var _response = response.response;
            var _numLikes = $("#likes");
            if (_response === "like") {
                $("#like-group").css('color', '#ec407a');
                $(_numLikes).find("strong").html(parseInt($(_numLikes).find("strong").html()) + 1);
            } else if (_response === "no_like") {
                $("#like-group").css('color', '#46494c');
                if ($(_numLikes).find("strong").html() > 0) {
                    $(_numLikes).find("strong").html(parseInt($(_numLikes).find("strong").html()) - 1);
                }
            } else {
                swal({
                    title: "¡Ups!",
                    text: "Hay un error con tu petición, intentalo de nuevo mas tarde.",
                    customClass: 'default-div'
                });
            }
        }, error: function (rs, e) {

        }
    });
}

function AJAX_submit_group_publication(obj_form, type, pks) {
    var form = new FormData($(obj_form).get(0));
    form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    type = typeof type !== 'undefined' ? type : "reply"; //default para type
    $.ajax({
        url: '/publication_g/',
        type: 'POST',
        data: form,
        async: true,
        dataType: "json",
        contentType: false,
        enctype: 'multipart/form-data',
        processData: false,
        success: function (data) {
            var response = data.response;
            var msg = data.msg;

            if (response === true && (typeof(msg) !== 'undefined' && msg !== null)) {
                swal({
                    title: "",
                    text: msg,
                    customClass: 'default-div',
                    type: "success"
                });
            } else if (response === true) {

            } else {
                swal({
                    title: "",
                    text: "Failed to publish",
                    customClass: 'default-div',
                    type: "error"
                });
            }
            if (type === "reply") {
                var caja_comentarios = $('#caja-comentario-' + pks);
                $(caja_comentarios).find('.message-reply').val(''); // Borramos contenido
                $(caja_comentarios).fadeOut();
            } else if (type === "publication") {
                $('#group_form_wrapper').fadeOut("fast"); // Ocultamos el DIV al publicar un mensaje.
                $('#group_publication_form').val('');
            }
        },
        error: function (data, textStatus) {
            var response = $.parseJSON(data.responseText);
            var error_msg = response.error[0];
            var type_error = response.type_error;

            if (type_error === 'incorrent_data') {
                swal({
                    title: '¡Ups!',
                    text: error_msg, // rs.responseText,
                    customClass: 'default-div',
                    type: "error"
                });
            } else {
                swal({
                    title: '¡Ups!',
                    text: 'Revisa el contenido de tu mensaje', // rs.responseText,
                    customClass: 'default-div',
                    type: "error"
                });
            }
        }
    }).done(function () {

    })
}

function AJAX_remove_group_request() {
    var slug = $("#group-profile").data('id');
    $.ajax({
        type: 'POST',
        url: '/remove_group_request/',
        data: {
            'slug': slug,
            'status': 'cancel',
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (data) {
            var response = data.response;
            if (response == true) {
                $('#cancel_group_request').replaceWith('<span id="follow-group" class="material-icons group-follow" title="Seguir">add</span>');
            } else if (response == false) {
                swal({
                    title: "¡Ups!",
                    text: "Ha surgido un error, inténtalo de nuevo más tarde :-(",
                    customClass: 'default-div'
                });
            }
        }, error: function (rs, e) {
            // swal(rs.responseText + " " + e);
        }
    });
}


function AJAX_kick_member(id, group_id) {
    $.ajax({
        type: 'POST',
        url: '/kick_member/',
        data: {
            'id': id,
            'group_id': group_id,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (data) {
            var response = data.response;
            if (response === 'kicked') {
                $('#member-' + id).remove();
            } else if (response === 'is_owner') {
                swal({
                    title: "¡Ups!",
                    text: "¿Estas intentando expulsarte de tu grupo?",
                    customClass: 'default-div',
                    type: 'error',
                });
            } else if (response === 'error') {
                swal({
                    title: "¡Ups!",
                    text: "Ha surgido un error, inténtalo de nuevo más tarde :-(",
                    customClass: 'default-div'
                });
            }
        }, error: function (rs, e) {
            // swal(rs.responseText + " " + e);
        }
    });
}

function AJAX_delete_group_publication(id, board_group) {
    var data = {
        'id': id,
        'board_group': board_group,
        'csrfmiddlewaretoken': csrftoken
    };
    $.ajax({
        url: '/publication/group/delete/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            // borrar caja publicacion
            if (data.response === true) {
                $('#pub-' + id).fadeToggle("fast", function () {
                    $(this).remove();
                });
                /*
                if (data.shared_pub_id) {
                    var shared_btn = $('#share-' + data.shared_pub_id);
                    var shared_btn_child = shared_btn.children();
                    var countShares = shared_btn_child.text();
                    if (!countShares || (Math.floor(countShares) == countShares && $.isNumeric(countShares))) {
                        countShares--;
                        countShares > 0 ? shared_btn_child(countShares) : shared_btn_child.text('');
                    }
                    shared_btn.attr('class', 'add-timeline');
                    shared_btn.css('color', '#555');
                }
                */
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

function AJAX_add_like_group_publication(caja_publicacion, heart, type) {
    var id_pub;
    if (type.localeCompare("publication") === 0) {
        id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
    }

    var data = {
        'pk': id_pub,
        'csrfmiddlewaretoken': csrftoken
    };

    $.ajax({
        url: '/publication/group/add_like/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            var response = data.response;
            var status = data.statuslike;
            var numLikes = $(heart).find('.like-value');
            var countLikes = numLikes.text();
            if (response === true) {
                if (!countLikes || (Math.floor(countLikes) === parseInt(countLikes) && $.isNumeric(countLikes))) {
                    if (status === 1) {
                        $(heart).css('color', '#f06292');
                        countLikes++;
                    } else if (status === 2) {
                        $(heart).css('color', '#555');
                        countLikes--;
                    } else if (status === 3) {
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
                    if (status === 1)
                        $(heart).css('color', '#f06292');
                    if (status === 2)
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

function AJAX_add_hate_group_publication(caja_publicacion, heart, type) {
    var id_pub;
    if (type.localeCompare("publication") === 0) {
        id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
    }

    var data = {
        'pk': id_pub,
        'csrfmiddlewaretoken': csrftoken
    };

    $.ajax({
        url: '/publication/group/add_hate/',
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
                        var likes = likesObj.find(".like-value");
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

function AJAX_edit_group_publication(pub, content) {
    var data = {
        'id': pub,
        'content': content,
        'csrfmiddlewaretoken': csrftoken
    };
    $.ajax({
        url: '/publication/group/edit/',
        type: 'POST',
        dataType: 'json',
        data: data,

        success: function (data) {
            var response = data.response;
            console.log(data);
            // borrar caja publicacion
            if (response === true) {
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


function AJAX_load_descendants_group(pub, loader, page, btn) {
    if (loadDescendantsRunning) {
        return;
    }

    $.ajax({
        url: page,
        type: 'GET',
        dataType: 'json',
        beforeSend: function() {
            $(loader).fadeIn();
            loadDescendantsRunning = true;
        },
        success: function (data) {
            var $existing = $('#pub-' + pub);
            var $children_list = $existing.find('.children').first();
            if (!$children_list.length) {
                $children_list = $existing.find('.wrapper-reply').after('<ul class="children"></ul>');
            }
            $children_list.append(data.content);
            btn.attr('href', '/publication/group/load/replies/?page=' + data.page + '&pubid=' + pub);
            var $child_count = btn.find('.child_count');
            var $result_child_count = parseInt($child_count.html(), 10) - data.childs;
            if ($result_child_count > 0)
                $($child_count).html($result_child_count);
            else
                btn.remove();
        },
        complete: function () {
            $(loader).fadeOut();
            loadDescendantsRunning = false;
        },
        error: function (rs, e) {
            console.log(e);
        }
    });
}