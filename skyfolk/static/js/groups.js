$(function () {
    var _group_profile = $('#group-profile');

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
    $('#group_form_wrapper .close').click(function() {
        $('#group_form_wrapper').hide();
    });
    
    /* Submit publication */
    $('#group_form_wrapper').find('#group_publication').on('submit', function (event) {
        event.preventDefault();
        var form = $(this);
        AJAX_submit_group_publication(form, 'publication');
    });
    $(_group_profile).on('click', '#cancel_group_request', function() {
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
    $('.kick-member').click(function() {
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
            closeOnConfirm: true
        }, function(isConfirm) {
            if (isConfirm) {
                AJAX_kick_member(id, group_id);
            }
        });
    });
    /* Borrar publicacion */
    $('#tab-comentarios').on('click', '.options_comentarios .trash-comment', function () {
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
    $('#tab-comentarios').on('click', '.options_comentarios .fa-reply', function () {
        var id_ = $(this).attr("id").slice(6);
        $("#" + id_).slideToggle("fast");
    });
    /* Submit reply publication */
    $('#tab-comentarios').on('click', '.group_reply', function (event) {
        event.preventDefault();
        var form = $(this).closest('form'); 
        var parent_pk = $(this).attr('id').split('-')[1];
        AJAX_submit_group_publication(form, 'reply', parent_pk);
    });
});// end document ready



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
                $('#follow-group').attr({
                    "id": "unfollow-group",
                    "class": "fa fa-remove group-follow",
                    "style": "color: #29b203;"
                });
            } else if (_response === "own_group") {
                swal({
                    title: "¡Ups!",
                    text: "¡No puedes seguir a tu propio grupo!",
                    customClass: 'default-div'
                });
            } else if (_response === "in_progress") {
                $('#follow-group').replaceWith('<span class="fa fa-clock-o" id="cancel_group_request" title="En proceso">' + ' ' + '</span>');
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
                $('#unfollow-group').attr({
                    "id": "follow-group",
                    "class": "fa fa-plus group-follow",
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
            } else if (_response === "own_group") {
                swal({
                    title: "¡Ups!",
                    text: "¡No puedes dar like a tu propio grupo!",
                    customClass: 'default-div'
                });
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
                $('#cancel_group_request').replaceWith('<span id="follow-group" class="fa fa-plus group-follow" title="Seguir"></span>');
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
                $('#member-'+id).remove();
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
    console.log(id + ' ' + board_group);
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
            if (data.response == true) {
                $('#pub-'+id).fadeToggle("fast");
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
