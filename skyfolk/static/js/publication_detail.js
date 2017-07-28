var max_height_comment = 60;

$(document).ready(function () {

    var thread = $(this);
    var wrapper_shared_pub = $('#share-publication-wrapper');

    /* Abrir respuesta a comentario */
    $(thread).on('click', '.options_comentarios .fa-reply', function () {
        var id_ = $(this).attr("id").slice(6);
        $("#" + id_).slideToggle("fast");
    });

    /* Submit reply publication */
    $(thread).on('click', 'button.enviar', function (event) {
        event.preventDefault();
        var parent_pk = $(this).attr('id').split('-')[1];
        var form = $(this).parent();
        $(form).find('input[name=parent]').val(parent_pk);
        var user_pk = $(form).find('input[name=author]').val();
        var owner_pk = $(form).find('input[name=board_owner]').val();
        var pks = [user_pk, owner_pk, parent_pk];
        AJAX_submit_publication(form, 'reply', pks);
    });

    /* Agregar skyline */
    $(this).on('click', '.options_comentarios .add-timeline', function () {
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
        AJAX_add_timeline_detail(pub_id, tag, content);
    });

    /* Cerrar div de compartir publicacion */
    $('#close_share_publication').click(function () {
        $(wrapper_shared_pub).hide();
    });

    /* Eliminar skyline */
    $(this).on('click', '.options_comentarios .remove-timeline', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var tag = this;
        AJAX_add_timeline_detail($(caja_publicacion).attr('id').split('-')[1], tag, null);
    });

    /* Añadir me gusta a comentario */
    $(thread).on('click', '.options_comentarios .like-comment', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        AJAX_add_like_detail(caja_publicacion, heart, "publication");
    });

    /* Añadir no me gusta a comentario */
    $(thread).on('click', '.options_comentarios .hate-comment', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        AJAX_add_hate_detail(caja_publicacion, heart, "publication");
    });

    /* Borrar publicacion */
    $(thread).on('click', '.options_comentarios .fa-trash', function () {
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
                AJAX_delete_publication_detail(caja_publicacion);
            }
        });
    });
    
    /* Editar comentario */
    $(thread).on('click', '.edit-comment', function () {
        var id = $(this).attr('data-id');
        $("#author-controls-" + id).slideToggle("fast");
    });

    $(thread).on('click', '.edit-comment-btn', function (event) {
        event.preventDefault();
        var id = $(this).attr('data-id');
        var content = $(this).closest('#author-controls-' + id).find('#id_caption-' + id).val();
        AJAX_edit_publication_detail(id, content);
    });
}); // END DOCUMENT


function AJAX_delete_publication_detail(caja_publicacion) {
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
            if (data.response == true) {
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

function AJAX_add_like_detail(caja_publicacion, heart, type) {
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
            var numLikes = $(heart).find('.like-value');
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
                        } else {
                            hates.text(countHates);
                        }
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

function AJAX_add_hate_detail(caja_publicacion, heart, type) {
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

function AJAX_add_timeline_detail(pub_id, tag, data_pub) {

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
                    $(tag).attr("class", "remove-timeline");
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
                    $(tag).attr("class", "add-timeline");
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

/* EDIT PUBLICATION */
function AJAX_edit_publication_detail(pub, content) {
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
