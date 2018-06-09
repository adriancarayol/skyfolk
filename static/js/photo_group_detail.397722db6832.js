var max_height_comment = 60;

$(document).ready(function () {
    var tab_messages = $(this);
    var wrapper_shared_pub = $('#share-publication-wrapper');

    /* Show more - Show less */
    $(tab_messages).find('.wrapper').each(function () {
        var comment = $(this).find('.wrp-comment');
        var show = $(this).find('.show-more a');

        if ($(comment).height() > max_height_comment) {
            $(show).show();
            $(comment).css('height', '2.6em');
        } else {
            //$(show).css('display', 'none');
        }
    });

    $(tab_messages).on('click', '.show-more a', function () {
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


    $(tab_messages).on('click', '.wrapper .zoom-pub', function () {
        var caja_pub = $(this).closest('.wrapper');
        expandComment(caja_pub);
    });

    function expandComment(caja_pub) {
        var id_pub = $(caja_pub).attr('id').split('-')[1];  // obtengo id
        window.location.href = '/group/multimedia/publication/detail/' + id_pub;
    }

    $(tab_messages).on('click', '.options_comentarios .add-timeline', function () {
        var tag = $(this);
        wrapper_shared_pub.find('#id_pk').val($(tag).data('id'));
        wrapper_shared_pub.show();
    });

    /* Compartir a skyline */
    $(wrapper_shared_pub).find('#share_publication_form').on('submit', function (event) {
        event.preventDefault();
        var content = $(this).serialize();
        var pub_id = wrapper_shared_pub.find('#id_pk').val();
        var tag = $('#pub-' + pub_id).find('.add-timeline').first();
        AJAX_add_timeline_gallery(pub_id, tag, content);
    });

    /* Cerrar div de compartir publicacion */
    $('#close_share_publication').click(function () {
        wrapper_shared_pub.hide();
        $wrapper_shared_pub.find('#id_pk').val('');
    });

    /* Eliminar skyline */
    $(tab_messages).on('click', '.options_comentarios .remove-timeline', function () {
        var tag = $(this);
        AJAX_remove_timeline_gallery(tag.data('id'), tag);
    });


    /* Abrir respuesta a comentario */
    $(tab_messages).on('click', '.options_comentarios .reply-comment', function () {
        var id_ = $(this).attr("id").slice(6);
        $("#" + id_).slideToggle("fast");
    });

    /* Submit reply publication */
    $(tab_messages).on('click', 'button.enviar', function (event) {
        event.preventDefault();
        var parent_pk = $(this).attr('id').split('-')[1];
        var form = $(this).parent();
        AJAX_submit_multimedia_group_photo_publication(form, 'reply', parent_pk);
    });


    /* Añadir me gusta a comentario */
    $(tab_messages).on('click', '.options_comentarios .like-comment', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = $(this);
        AJAX_add_like_group_gallery(caja_publicacion, heart, "publication");
    });

    /* Añadir no me gusta a comentario */
    $(tab_messages).on('click', '.options_comentarios .hate-comment', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = $(this);
        AJAX_add_hate_group_gallery(caja_publicacion, heart, "publication");
    });

    /* Borrar publicacion */
    $(tab_messages).on('click', '.options_comentarios .trash-comment', function () {
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
                AJAX_delete_publication_group_gallery(caja_publicacion);
            }
        });
    });


    $("#tab-messages").find('#message-photo-form').on('submit', function (event) {
        event.preventDefault();
        var form = $('#messages-wrapper').find('#message-photo-form');
        AJAX_submit_multimedia_group_photo_publication(form, 'publication');
    });

    /* Editar comentario */
    $(tab_messages).on('click', '.edit-comment', function () {
        var id = $(this).attr('data-id');
        $("#p_author-controls-" + id).slideToggle("fast");
    });

    $(tab_messages).on('click', '.edit-comment-btn', function (event) {
        event.preventDefault();
        var edit = $(this).closest('form').serialize();
        AJAX_edit_publication_group_gallery(edit);
    });

    $(tab_messages).on('click', '.load_more_descendants', function (e) {
        e.preventDefault();
        var loader = $(this).next().find('.load_publications_descendants');
        var pub_id = $(this).attr("data-id");
        var page = $('.page_for_' + pub_id).last().val();
        if (typeof page === 'undefined')
            page = 1;
        AJAX_load_descendants_group_gallery(pub_id, loader, page, this);
    });

    $('#messages-wrapper').on('click', '#load-comments', function(e) {
        e.preventDefault();
        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            success : function(data)
            {
                $('#load-comments').remove();
                $('.loading_publications').before(data);
            }
        });
    });

});


function AJAX_submit_multimedia_group_photo_publication(obj_form, type, pks) {
    var form = new FormData($(obj_form).get(0));
    form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    type = typeof type !== 'undefined' ? type : "reply"; //default para type
    $.ajax({
        url: '/group/multimedia/publication/',
        type: 'POST',
        data: form,
        async: true,
        dataType: "json",
        contentType: false,
        enctype: 'multipart/form-data',
        processData: false,
        success: function (data) {
            var msg = data.msg;
            if (typeof(msg) !== 'undefined' && msg !== null) {
                swal({
                    title: "",
                    text: msg,
                    customClass: 'default-div',
                    type: "success"
                });
            }
            if (type === "reply") {
                var caja_comentarios = $('#caja-comentario-' + pks);
                $(caja_comentarios).find('.message-reply').val(''); // Borramos contenido
                $(caja_comentarios).fadeOut();
            } else if (type === "publication") {
                $('#message-photo').val(''); // Ocultamos el DIV al publicar un mensaje.
            }
        }, error: function (data, textStatus, jqXHR) {
            var errors = [];
            $.each(data.responseJSON, function (i, val) {
                errors.push(val);
            });
            swal({
                title: "Tenemos un problema...",
                customClass: 'default-div',
                text: errors.join(),
                timer: 4000,
                showConfirmButton: true
            });
        }
    }).done(function () {

    })
}

function AJAX_delete_publication_group_gallery(caja_publicacion) {
    var id_pub = $(caja_publicacion).attr('id').split('-')[1];  // obtengo id
    var id_user = $(caja_publicacion).data('id'); // obtengo id
    var data = {
        userprofile_id: id_user,
        publication_id: id_pub,
        'csrfmiddlewaretoken': csrftoken
    };

    $.ajax({
        url: '/group/multimedia/publication/delete/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            // borrar caja publicacion
            if (data === true) {
                $(caja_publicacion).closest('.infinite-item').remove();
                $(".infinite-container").find(`[data-parent='${id_pub}']`).closest('.infinite-item').remove();

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

function AJAX_add_like_group_gallery(caja_publicacion, heart, type) {
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
        url: '/group/multimedia/publication/add_like/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            var response = data.response;
            var status = data.statuslike;
            var numLikes = heart.find('.like-value');
            var countLikes = numLikes.text();
            if (response == true) {
                if (!countLikes || (Math.floor(countLikes) == countLikes && $.isNumeric(countLikes))) {
                    if (status == 1) {
                        heart.css('color', '#f06292');
                        countLikes++;
                    } else if (status == 2) {
                        heart.css('color', '#555');
                        countLikes--;
                    } else if (status == 3) {
                        heart.css('color', '#f06292');
                        var hatesObj = heart.prev();
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
                        heart.css('color', '#f06292');
                    if (status == 2)
                        heart.css('color', '#555');
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

function AJAX_add_hate_group_gallery(caja_publicacion, heart, type) {
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
        url: '/group/multimedia/publication/add_hate/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            var statusOk = 1;
            var statusNo = 2;
            var statusInLike = 3;
            var response = data.response;
            var status = data.statuslike;
            var numHates = heart.find(".hate-value");
            var countHates = numHates.text();
            if (response == true) {
                if (!countHates || (Math.floor(countHates) == countHates && $.isNumeric(countHates))) {
                    if (status === statusOk) {
                        heart.css('color', '#ba68c8');
                        countHates++;
                    } else if (status === statusNo) {
                        heart.css('color', '#555');
                        countHates--;
                    } else if (status === statusInLike) {
                        heart.css('color', '#ba68c8');
                        countHates++;
                        var likesObj = heart.next();
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
                        heart.css('color', '#ba68c8');
                    } else if (status === statusNo) {
                        heart.css('color', '#555');
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

/* EDIT PUBLICATION */
function AJAX_edit_publication_group_gallery(data) {
    $.ajax({
        url: '/group/multimedia/publication/edit/',
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

function AJAX_load_descendants_group_gallery(pub, loader, page, btn) {
    $.ajax({
        url: '/group/multimedia/publication/load_descendants/?pubid=' + pub + '&page=' + page,
        type: 'GET',
        dataType: 'html',
        beforeSend: function() {
            $(loader).fadeIn();
        },
        success: function (data) {
            var $existing = $('#pub-' + pub);
            var $children_list = $existing.find('.children').first();
            if (!$children_list.length) {
                $existing.find('.wrapper-reply').after('<ul class="children"></ul>');
                $children_list = $existing.find('.children').first();
            }

            $children_list.append(data);
            var $child_count = $(btn).find('.child_count');
            var $result_child_count = parseInt($child_count.html(), 10) - $('.childs_for_' + pub).last().val();
            if ($result_child_count > 0)
                $($child_count).html($result_child_count);
            else
                $(btn).remove();
        },
        complete: function () {
            $(loader).fadeOut();
        },
        error: function (rs, e) {
        }
    });
}
