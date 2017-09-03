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
        window.location.href = '/publication_pdetail/' + id_pub;
    }

    $(tab_messages).on('click', '.options_comentarios .add-timeline', function () {
        var tag = $(this);
        $(wrapper_shared_pub).attr('data-id', tag.attr('data-id'));
        $(wrapper_shared_pub).show();
    });

    /* Compartir a skyline */
    $(wrapper_shared_pub).find('#share_publication_form').on('submit', function (event) {
        event.preventDefault();
        var content = $(wrapper_shared_pub).find('#shared_comment_content').val();
        var pub_id = $(wrapper_shared_pub).attr('data-id');
        var tag = $('#pub-' + pub_id).find('.add-timeline').first();
        AJAX_add_timeline_gallery(pub_id, tag, content);
    });

    /* Cerrar div de compartir publicacion */
    $('#close_share_publication').click(function () {
        $(wrapper_shared_pub).hide();
    });

    /* Eliminar skyline */
    $(tab_messages).on('click', '.options_comentarios .remove-timeline', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var tag = $(this);
        AJAX_add_timeline_gallery($(caja_publicacion).attr('id').split('-')[1], tag, null);
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
        AJAX_submit_photo_publication(form, 'reply', parent_pk);
    });


    /* Añadir me gusta a comentario */
    $(tab_messages).on('click', '.options_comentarios .like-comment', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = $(this);
        AJAX_add_like_gallery(caja_publicacion, heart, "publication");
    });

    /* Añadir no me gusta a comentario */
    $(tab_messages).on('click', '.options_comentarios .hate-comment', function () {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = $(this);
        AJAX_add_hate_gallery(caja_publicacion, heart, "publication");
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
                AJAX_delete_publication_gallery(caja_publicacion);
            }
        });
    });

    /* Editar comentario */
    $(tab_messages).on('click', '.edit-comment', function () {
        var id = $(this).attr('data-id');
        $("#p_author-controls-" + id).slideToggle("fast");
    });

    $(tab_messages).on('click', '.edit-comment-btn', function (event) {
        event.preventDefault();
        var id = $(this).attr('data-id');
        var content = $(this).closest('#p_author-controls-' + id).find('#id_caption-' + id).val();
        AJAX_edit_publication_gallery(id, content);
    });

    $(tab_messages).on('click', '.load_more_descendants', function (e) {
        e.preventDefault();
        var loader = $(this).next().find('.load_publications_descendants');
        var pub_id = $(this).attr("data-id");
        var page = $('.page_for_' + pub_id).last().val();
        if (typeof page === 'undefined')
            page = 1;
        AJAX_load_descendants_gallery(pub_id, loader, page, this);
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


function AJAX_submit_photo_publication(obj_form, type, pks) {
    var form = new FormData($(obj_form).get(0));
    form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    type = typeof type !== 'undefined' ? type : "reply"; //default para type
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
                var caja_comentarios = $('#caja-comentario-' + pks);
                $(caja_comentarios).find('.message-reply').val(''); // Borramos contenido
                $(caja_comentarios).fadeOut();
            } else if (type === "publication") {
                $('#message-photo').val(''); // Ocultamos el DIV al publicar un mensaje.
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

function AJAX_delete_publication_gallery(caja_publicacion) {
    var id_pub = $(caja_publicacion).attr('id').split('-')[1];  // obtengo id
    var id_user = $(caja_publicacion).data('id'); // obtengo id
    var data = {
        userprofile_id: id_user,
        publication_id: id_pub,
        'csrfmiddlewaretoken': csrftoken
    };

    $.ajax({
        url: '/publication_p/delete/',
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

function AJAX_add_like_gallery(caja_publicacion, heart, type) {
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
        url: '/publication_p/add_like/',
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

function AJAX_add_hate_gallery(caja_publicacion, heart, type) {
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
        url: '/publication_p/add_hate/',
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

function AJAX_add_timeline_gallery(pub_id, tag, data_pub) {

    var data = {
        'publication_id': pub_id,
        'content': data_pub,
        'csrfmiddlewaretoken': csrftoken
    };

    var shared_tag = tag.find('.share-values');
    var count_shared = $(shared_tag).text();
    count_shared = count_shared.replace(/ /g, '');

    $.ajax({
        url: '/publication_p/share/publication/',
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
                    tag.attr("class", "remove-timeline");
                    tag.css('color', '#bbdefb');
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
                    tag.attr("class", "add-timeline");
                    tag.css('color', '#555');
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
function AJAX_edit_publication_gallery(pub, content) {
    var data = {
        'id': pub,
        'content': content,
        'csrfmiddlewaretoken': csrftoken
    };
    $.ajax({
        url: '/publication_p/edit/',
        type: 'POST',
        dataType: 'json',
        data: data,

        success: function (data) {
            var response = data.data;
            console.log(data.data);
            // borrar caja publicacion
            if (response == true) {
                $('#p_author-controls-' + pub).fadeToggle("fast");
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

function AJAX_load_descendants_gallery(pub, loader, page, btn) {
    $.ajax({
        url: '/publication_p/load_descendants/?pubid=' + pub + '&page=' + page,
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
