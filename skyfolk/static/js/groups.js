$(function () {
    var _group_profile = $('#group-profile');
    var $tab_commentarios = $('#tab-comentarios');
    var $wrapper_shared_pub = $('#share-publication-wrapper');

    $("#li-tab-themes").click(function () {
        $('#tab-themes').css({
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
        var publication_wrapper = $(this).closest('.infinite-item');
        console.log(publication_wrapper);
        var id = $(publication_wrapper).attr('id').split('-')[1];
        var board_group = $(publication_wrapper).data('id');
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
        Materialize.updateTextFields();
        var id = $(this).attr('data-id');
        $("#author-controls-" + id).slideToggle("fast");
    });

    $tab_commentarios.on('click', '.edit-comment-btn', function (event) {
        event.preventDefault();
        var edit = $(this).closest('form').serialize();
        AJAX_edit_group_publication(edit);
    });

    $tab_commentarios.on('click', '.zoom-pub', function () {
        var id = $(this).attr('id').split('-')[1];
        window.location.href = '/group/publication/' + id;
    });

    $tab_commentarios.on('click', '.load_more_publications', function (e) {
        e.preventDefault();
        var loader = $(this).next().find('.load_publications_descendants');
        var pub_id = $(this).data('id');
        var page = $(this).attr('href');
        AJAX_load_descendants_group(pub_id, loader, page, $(this));
    });

    /* Agregar skyline */
    $(this).on('click', '.add-timeline', function (e) {
        var tag = $(this);
        $wrapper_shared_pub.find('#id_pk').val($(tag).data('id'));
        $wrapper_shared_pub.show();
        $("html, body").animate({scrollTop: 0}, "slow");
    });

    /* Compartir a skyline */
    $wrapper_shared_pub.find('#share_publication_form').on('submit', function (event) {
        event.preventDefault();
        var content = $(this).serialize();
        content += '&csrfmiddlewaretoken=' + csrftoken;
        var pub_id = $wrapper_shared_pub.find('#id_pk').val();
        var tag = $('#pub-' + pub_id).find('.add-timeline').first();
        AJAX_add_publication_to_skyline(pub_id, tag, content);
    });

    /* Cerrar div de compartir publicacion */
    $('#close_share_publication').click(function () {
        $wrapper_shared_pub.hide();
        $wrapper_shared_pub.find('#id_pk').val('');
    });

    /* Eliminar skyline */
    $(this).on('click', '.remove-timeline', function () {
        var tag = $(this);
        AJAX_remove_publication_from_skyline(tag.data('id'), tag);
    });
    /* THEMES */
    /* Create theme */
    $(this).on('submit', '#new_group_theme', function (e) {
        e.preventDefault();
        var form = $(this);
        var data = new FormData(form[0]);
        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            success: function (data, textStatus, jqXHR) {
                Materialize.toast('¡Tema creado con éxito!', 4000); // 4000 is the duration of the toast
                form.trigger('reset');
                form.closest('.container_group_theme').hide();
            },
            error: function (data, textStatus, jqXHR) {
                swal({
                    title: "Tenemos un problema...",
                    customClass: 'default-div',
                    text: "Hubo un problema con su petición.",
                    timer: 4000,
                    showConfirmButton: true
                });
            }
        });
    });

    $(this).on('click', '.open_theme_form', function () {
        $('.container_group_theme').toggle();
    });

    $(this).on('click', '.like-theme', function () {
        var pk = $(this).closest('.theme').data('id');
        var $parent_btn = $(this);
        var $like_btn = $(this).find('.like-theme-value');
        var countLikes = parseInt($like_btn.text()) || 0;
        $.ajax({
            type: 'POST',
            url: '/groups/like/theme/',
            data: {
                'pk': pk,
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function (data) {
                var _response = data.response;
                var _status = data.status;
                var _in_hate = data.in_hate;
                if (_response === true) {
                    if (_in_hate === true) {
                        var $hate_btn = $parent_btn.next();
                        var $hate_val = $hate_btn.find('.hate-theme-value');
                        var countHates = parseInt($hate_val.text()) || 0;
                        countHates--;
                        $hate_val.text(countHates > 0 ? countHates : '');
                        $hate_btn.css('color', '#555');
                    }
                    if (_status === 2) {
                        $parent_btn.css('color', 'rgb(240, 98, 146)');
                        countLikes++;
                    } else if (_status === 1) {
                        $parent_btn.css('color', '#555');
                        countLikes--;
                    }
                    if (countLikes <= 0) {
                        $like_btn.text('');
                    } else {
                        $like_btn.text(countLikes);
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
            }, error: function (data, textStatus, jqXHR) {
                swal({
                    title: "Tenemos un problema...",
                    customClass: 'default-div',
                    text: "Hubo un problema con su petición.",
                    timer: 4000,
                    showConfirmButton: true
                });
            }
        });
    });
    $(this).on('click', '.hate-theme', function () {
        var pk = $(this).closest('.theme').data('id');
        var $parent_btn = $(this);
        var $hate_btn = $(this).find('.hate-theme-value');
        var countHates = parseInt($hate_btn.text()) || 0;
        $.ajax({
            type: 'POST',
            url: '/groups/hate/theme/',
            data: {
                'pk': pk,
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: 'json',
            success: function (data) {
                var _response = data.response;
                var _status = data.status;
                var _in_like = data.in_like;
                if (_response === true) {
                    if (_in_like === true) {
                        var $like_btn = $parent_btn.prev();
                        var $like_val = $like_btn.find('.like-theme-value');
                        var countLikes = parseInt($like_val.text()) || 0;
                        countLikes--;
                        $like_val.text(countLikes > 0 ? countLikes : '');
                        $like_btn.css('color', '#555');
                    }
                    if (_status === 2) {
                        $parent_btn.css('color', 'rgb(186, 104, 200)');
                        countHates++;
                    } else if (_status === 1) {
                        $parent_btn.css('color', '#555');
                        countHates--;
                    }
                    if (countHates <= 0) {
                        $hate_btn.text('');
                    } else {
                        $hate_btn.text(countHates);
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
            }, error: function (data, textStatus, jqXHR) {
                swal({
                    title: "Tenemos un problema...",
                    customClass: 'default-div',
                    text: "Hubo un problema con su petición.",
                    timer: 4000,
                    showConfirmButton: true
                });
            }
        });
    });
    $('.theme').on('click', '.reply_theme', function () {
        var id_ = $(this).closest('.theme').data('id');
        $("#caja-theme-" + id_).toggle();
    });

    $('.theme-publications').on('click', '.reply-comment', function () {
        var id_ = $(this).attr('id').split('-')[3];
        $("#caja-comentario-" + id_).toggle();
    });

    /* Submit reply publication */
    $('.theme, .theme-publications').on('click', '.send_reply_theme', function (event) {
        event.preventDefault();
        AJAX_submit_theme_publication($(this).closest('form'));
    });

    $('.theme-publications').on('click', '.like-comment', function () {
        var pub_box = $(this).closest('.wrapper');
        var $parent_btn = $(this);
        var $like_btn = $(this).closest('.score-controls').find('.score-comment');
        var countLikes = $like_btn.text();
        $.ajax({
            url: '/group/publication/theme/like/',
            type: 'POST',
            data: {
                'pk': pub_box.data('id'),
                'csrfmiddlewaretoken': csrftoken
            },
            async: true,
            dataType: "json",
            success: function (data) {
                var _response = data.response;
                var _status = data.status;
                var _in_hate = data.in_hate;
                if (_response === true) {
                    if (!countLikes || (Math.floor(countLikes) == countLikes && $.isNumeric(countLikes))) {
                        countLikes = parseInt(countLikes);
                        if (_in_hate === true) {
                            countLikes = countLikes + 2;
                            let hateObj = $($parent_btn).closest('.score-controls').find('.hate-comment');
                            $($parent_btn).css('border-bottom', "20px solid #66bb6a");
                            $(hateObj).css('border-top', "20px solid");
                        } else if (_status === 2) {
                            countLikes++;
                            $($parent_btn).css('border-bottom', "20px solid #66bb6a");
                        } else if (_status === 1) {
                            countLikes--;
                            $($parent_btn).css('border-bottom', "20px solid");
                        }
                        $like_btn.text(countLikes);
                    }
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
        });
    });

    $('.theme-publications').on('click', '.hate-comment', function () {
        var pub_box = $(this).closest('.wrapper');
        var $parent_btn = $(this);
        var $hate_btn = $(this).closest('.score-controls').find('.score-comment');
        var countHates = $hate_btn.text();
        $.ajax({
            url: '/group/publication/theme/hate/',
            type: 'POST',
            data: {
                'pk': pub_box.data('id')
            },
            async: true,
            dataType: "json",
            success: function (data) {
                var _response = data.response;
                var _status = data.status;
                var _in_like = data.in_like;

                if (_response === true) {
                    if (!countHates || (Math.floor(countHates) == countHates && $.isNumeric(countHates))) {
                        countHates = parseInt(countHates);
                        if (_in_like === true) {
                            countHates = countHates - 2;
                            let likesObj = $($parent_btn).closest('.score-controls').find('.like-comment');
                            $($parent_btn).css('border-top', "20px solid #ef5350");
                            $(likesObj).css('border-bottom', "20px solid");
                        } else if (_status === 2) {
                            countHates--;
                            $($parent_btn).css('border-top', "20px solid #ef5350");
                        } else if (_status === 1) {
                            countHates++;
                            $($parent_btn).css('border-top', "20px solid");
                        }
                        $hate_btn.text(countHates);
                    }
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
        });
    });

    $('.theme-publications').on('click', '.trash-comment', function () {
        var pub_box = $(this).closest('.wrapper');
        var pub_id = pub_box.data('id');
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
                $.ajax({
                    url: '/group/publication/theme/delete/',
                    type: 'POST',
                    data: {
                        'pk': pub_id
                    },
                    dataType: "json",
                    success: function (data) {
                        if (data.response === true) {
                            pub_box.closest('.infinite-item').remove();
                            $(".infinite-item").find(`[data-parent='${pub_id}']`).closest('.infinite-item').remove();
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
                });
            }
        });
    });
    $('.theme').on('click', '.delete-theme', function () {
        var theme_id = $(this).closest('.theme').data('id');
        swal({
            title: "Are you sure?",
            text: "You will not be able to recover this theme!",
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
                $.ajax({
                    url: '/groups/delete/theme/',
                    type: 'POST',
                    data: {
                        'pk': theme_id
                    },
                    dataType: "json",
                    success: function (data) {
                        if (data.response === true) {
                            location.href = data.redirect_url;
                        } else {
                            swal({
                                title: "Tenemos un problema...",
                                customClass: 'default-div',
                                text: "No puedes eliminar este tema.",
                                timer: 4000,
                                showConfirmButton: true
                            });
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
                });
            }
        });
    });

    $('#tab-themes').on('click', '.infinite-more-themes', function (e) {
        e.preventDefault();
        var _next = $(this).attr('href');
        $.get(_next, function (data, status) {
            var $load_themes = $('.load_themes');
            $load_themes.show();
            var _items = $(data).filter('.theme');
            $('.theme-list .infinite-more-themes').closest('.row').before(_items);
            $('.infinite-more-themes').replaceWith($(data).find('.infinite-more-themes'));
            $load_themes.hide();
        }).always(function () {

        });
    });

    $('.theme').on('click', '.edit-theme-btn', function () {
        $('.edit-theme-wrapper').toggle();
    });

    $('.theme').on('submit', '.edit-theme-form', function (e) {
        e.preventDefault();
        var form = $(this);
        var data = new FormData(form[0]);
        $.ajax({
            url: '/groups/edit/theme/',
            type: 'POST',
            dataType: 'json',
            processData: false,
            contentType: false,
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
                } else {
                    location.href = data.url;
                }
            },
            error: function (rs, e) {
            }
        });
    });

    $('.theme-publications').on('click', '.edit-comment', function () {
        Materialize.updateTextFields();
        var id = $(this).attr('data-id');
        $("#author-controls-" + id).slideToggle("fast");
    });

    $('.theme-publications').on('click', '.edit-comment-btn', function (event) {
        event.preventDefault();
        var edit = $(this).closest('form').serialize();
        AJAX_edit_theme_publication(edit);
    });

    $('#compose-new-no-comments').click(function () {
        $('#group_form_wrapper').toggle();
    });

    /* Config */
    $('#configurationOnProfile').click(function () {
        location.href = $(this).data('url');
    });

    $('#form-config-group').submit(function (e) {
        e.preventDefault();
        var url = $(this).attr('action');
        var data = new FormData($(this).get(0));

        $.ajax({
            url: url,
            type: 'POST',
            dataType: 'json',
            processData: false,
            contentType: false,
            data: data,

            success: function (data) {
                var response = data.data;

                if (response === false) {
                    swal({
                        title: "Fail",
                        customClass: 'default-div',
                        text: "Failed to edit publish.",
                        type: "error"
                    });
                } else {
                    Materialize.toast('La información de tu grupo se ha guardado correctamente.', 4000);
                }
            },
            error: function (rs, e) {
            }
        });
    });

    $('.interests').mouseenter(function () {
        var interests = $(this);
        var slug = interests.attr('data-slug');
        $.get("/group/" + slug + "/interests/", function (data) {
            interests.attr('data-tooltip', data.join());
        });
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
                $(_numLikes).find("b").html(parseInt($(_numLikes).find("b").html()) + 1);
            } else if (_response === "no_like") {
                $("#like-group").css('color', '#46494c');
                if ($(_numLikes).find("b").html() > 0) {
                    $(_numLikes).find("b").html(parseInt($(_numLikes).find("b").html()) - 1);
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
        url: '/group/new/publication/',
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
            if (typeof (msg) !== 'undefined' && msg !== null) {
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
                $('#group_form_wrapper').fadeOut("fast"); // Ocultamos el DIV al publicar un mensaje.
                $('#group_publication_form').val('');
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
        url: '/group/publication/delete/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            // borrar caja publicacion
            if (data.response === true) {
                $('#pub-' + id).fadeToggle("fast", function () {
                    $(this).remove();
                });
                $(".infinite-container").find(`[data-parent='${id}']`).remove();

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
        url: '/group/publication/add_like/',
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
        url: '/group/publication/add_hate/',
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

function AJAX_edit_group_publication(data) {
    $.ajax({
        url: '/group/publication/edit/',
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

function AJAX_edit_theme_publication(data) {
    $.ajax({
        url: '/group/publication/theme/edit/',
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

function AJAX_load_descendants_group(pub, loader, page, btn) {
    if (loadDescendantsRunning) {
        return;
    }

    $.ajax({
        url: page,
        type: 'GET',
        dataType: 'json',
        beforeSend: function () {
            $(loader).fadeIn();
            loadDescendantsRunning = true;
        },
        success: function (data) {
            var $existing = $('#list-publications').find('#pub-' + pub).first();
            var $children_list = $existing.find('.children').first();

            var parsed = $.parseHTML(data.content);

            for (var i = 0; i < parsed.length; i++) {
                var pub_id = $(parsed[i]).attr('id');
                var element = $('#' + pub_id);
                if (element.length) {
                    element.remove();
                }
            }

            $children_list.append(data.content);
            btn.attr('href', '/group/publication/load/replies/?page=' + data.page + '&pubid=' + pub);
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
            $('.dropdown-button').dropdown();
        },
        error: function (rs, e) {
            // console.log(e);
        }
    });
}

function AJAX_add_publication_to_skyline(pub_id, tag, data_pub) {

    var shared_tag = $(tag).find('.share-values');
    var count_shared = $(shared_tag).text();
    count_shared = count_shared.replace(/ /g, '');

    $.ajax({
        url: '/group/publication/share/',
        type: 'POST',
        dataType: 'json',
        data: data_pub,
        success: function (data) {
            var response = data.response;
            if (response === true) {
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

        }
    });
}

function AJAX_remove_publication_from_skyline(pub_id, tag) {

    var shared_tag = $(tag).find('.share-values');
    var count_shared = $(shared_tag).text();
    count_shared = count_shared.replace(/ /g, '');

    $.ajax({
        url: '/group/publication/delete/share/',
        type: 'POST',
        dataType: 'json',
        data: {
            'pk': pub_id,
            'csrfmiddlewaretoken': csrftoken
        },
        success: function (data) {
            var response = data.response;
            if (response === true) {
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

function AJAX_submit_theme_publication(form) {
    var form_data = new FormData(form.get(0));
    form_data.append('csrfmiddlewaretoken', getCookie('csrftoken'));

    $.ajax({
        url: '/group/publication/theme/reply/',
        type: 'POST',
        data: form_data,
        async: true,
        contentType: false,
        enctype: 'multipart/form-data',
        processData: false,
        success: function (response) {
            var parent = form_data.get('parent');
            var board_theme = form_data.get('board_theme');
            if (parent === null) {
                $('#caja-theme-' + board_theme).toggle();
            } else {
                $('#caja-comentario-' + parent).toggle();
            }
            var btnPubs = $('#theme-' + board_theme).find('.reply_theme .pubs-theme-value');
            var countPubs = parseInt(btnPubs.text()) || 0;
            countPubs++;
            btnPubs.text(countPubs);
            form.trigger("reset");
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
    });
}
