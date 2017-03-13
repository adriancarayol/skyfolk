var max_height_comment = 60;

$(document).ready(function () {

    var thread = $('#publication-thread');

    /* Show more - Show less */
    $(thread).find('.wrapper').each(function () {
        var comment = $(this).find('.wrp-comment');
        var show = $(this).find('.show-more a');

        if ($(comment).height() > max_height_comment) {
            $(show).show();
            $(comment).css('height', '2.6em');
        } else {
            //$(show).css('display', 'none');
        }
    });

    $('.wrapper').on('click', '.show-more a', function () {
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

    /* Abrir respuesta a comentario */
    $(thread).on('click', '#options-comments .fa-reply', function () {
        var id_ = $(this).attr("id").slice(6);
        $("#" + id_).slideToggle("fast");
    });

    /* Agregar timeline */
    $(thread).on('click', '#options-comments .fa-tag', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var tag = this;
        AJAX_add_timeline(caja_publicacion, tag, "publication");
    });

    /* Añadir me gusta a comentario */
    $(thread).on('click', '#options-comments #like-heart', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        AJAX_add_like(caja_publicacion, heart, "publication");
    });

    /* Añadir no me gusta a comentario */
    $(thread).on('click', '#options-comments #fa-hate', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        AJAX_add_hate(caja_publicacion, heart, "publication");
    });

    /* Borrar publicacion */
    $(thread).on('click', '#options-comments .fa-trash', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        console.log(caja_publicacion);
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
}); // END DOCUMENT


function AJAX_delete_publication(caja_publicacion) {
    var id_pub = $(caja_publicacion).attr('id').split('-')[1];  // obtengo id
    var id_user = $(caja_publicacion).data('id'); // obtengo id
    var data = {
        userprofile_id: id_user,
        publication_id: id_pub,
        'csrfmiddlewaretoken': csrftoken
    };

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