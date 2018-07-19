$(document).ready(function () {

    $('select').material_select();

    $('ul.tabs').tabs();

    $('#btn-upload-photo').on('click', function () {
        $('#upload_photo').toggle();
    });

    $('#close_upload_form, #close_upload_zip_form, #close_upload_video_form').on('click', function () {
        $('#upload_photo').toggle();
    });

    $('#del-photo').click(AJAX_delete_photo);

    $('#del-video').click(AJAX_delete_video);

    $("#edit-video").click(function () {
        $(this).text(function (i, text) {
            return text === "Editar" ? "No editar" : "Editar";
        });

        $('#wrapper-edit-form').toggle();

        return false;
    });

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


    $('#form-video').submit(function (e) {
        e.preventDefault();
        var url = $(this).attr('action');
        var data = new FormData($(this).get(0));
        $.ajax({
            url: url,
            type: 'POST',
            data: data,
            dataType: 'json',
            async: true,
            contentType: false,
            enctype: 'multipart/form-data',
            processData: false,
            success: function (data) {
                if (data.result === true) {
                    $('.container-gallery > .row').prepend(data.content);
                } else {
                    swal({
                        title: "¡Ups!.",
                        type: 'error',
                        text: data.message,
                        timer: 4000,
                        showConfirmButton: true
                    });
                }
            }, error: function (rs, e) {
                swal(rs.responseText + " " + e);
            }
        });
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

/* DELETE VIDEO */
function AJAX_delete_video() {
    var _id = $('.photo-body').attr('data-id');
    $.ajax({
        url: '/delete/video/',
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