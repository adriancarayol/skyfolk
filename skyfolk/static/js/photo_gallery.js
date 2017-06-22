$(document).ready(function () {

    $('select').material_select();

    $('ul.tabs').tabs();

    $('#btn-upload-photo').on('click', function () {
        $('#upload_photo').toggle();
    });

    $('#close_upload_form, #close_upload_zip_form').on('click', function () {
        $('#upload_photo').toggle();
    });

    $('#del-photo').click(AJAX_delete_photo);


    $("#edit-photo").click(function () {
        $(this).text(function (i, text) {
            return text === "Editar" ? "No editar" : "Editar";
        });

        $('#wrapper-edit-form').toggle();

        return false;
    });

    $('.tags-content').on('click', 'blockquote', function () {
        $(this).nextAll('input').click();
    });

    $('#crop-image').on('click', function () {
        $('#crop-image-preview').show();
        $('.avatar-form .is-cutted').val('true');
    });

    $('#crop-image-preview').find('.close-crop-image').on('click', function () {
        $('#crop-image-preview').hide();
        $('.avatar-form .is-cutted').val('false');
    });

    $('#crop-image-preview').find('#cut-done').on('click', function () {
        $('#crop-image-preview').hide();
        $('.avatar-form .is-cutted').val('true'); // Redundancia

    });

    $(this).on('keydown', function (e) {
        var key = e.keyCode || e.which;
        if (key == 27) {
            $('#upload_photo').hide();
            $('#crop-image-preview').hide();
            $('.avatar-form .is-cutted').val('false');
        }
    });

    $('#tab-messages').find('#message-photo-form').on('submit', function (event) {
        event.preventDefault();
        var form = $('#messages-wrapper').find('#message-photo-form');
        AJAX_submit_photo_publication(form, 'publication');
    });
}); // FIN DOCUMENT READY

/* DELETE OR EDIT PHOTO */
function AJAX_delete_photo() {
    var _id = $('.photo-body').attr('data-id');
    $.ajax({
        url: '/delete/photo/',
        type: 'DELETE',
        data: {
            'id': _id,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (json) {
            swal({
                title: "Photo was deleted.",
                text: json.msg,
                timer: 2500,
                showConfirmButton: true
            }, function () {
                window.location.replace('/multimedia/' + json.author + '/');
            });
        }, error: function (rs, e) {
            swal(rs.responseText + " " + e);
        }
    });
}

function AJAX_submit_photo_publication(obj_form, type, pks) {
    type = typeof type !== 'undefined' ? type : "reply"; //default para type
    var form = new FormData($(obj_form).get(0));
    $.ajax({
        url: '/publication_p/',
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
                $('#message-photo').val('');
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
