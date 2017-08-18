$(function () {
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
            console.log(_response);
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
                var caja_comentarios = $('#caja-comentario-' + pks[2]);
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
