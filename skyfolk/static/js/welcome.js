$(document).ready(function () {
    $('.chips-placeholder').material_chip({
        placeholder: 'Introduce un tema',
        secondaryPlaceholder: '+Música, +Cine...'
    });
    $('.progress').fadeOut();

    $('.chips').find('.input').css('background-color', 'white');

    var form = $('#submit-themes');

    form.submit(function () {
        var tags = $('.chips').material_chip('data');
        var text_tag = [];
        for (var i = 0; i < tags.length; i++) {
            text_tag.push(tags[i].tag);
        }
        var myCheckboxes = [];
        $("input:checked").each(function () {
            myCheckboxes.push($(this).val());
        });
        $.ajax({
            type: form.attr('method'),
            url: "/topics/",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'tags[]': text_tag,
                'choices[]': myCheckboxes
            },
            cache: false,
            dataType: "json",
            success: function (response) {
                if (response == "success") {
                    window.location.replace("/recommendations/");
                } else if (response == "with_spaces") {
                    swal({
                        title: "¡Un segundo!",
                        text: "Un interés no puede contener sólo espacios en blanco.",
                        customClass: 'default-div',
                        timer: 4000,
                        showConfirmButton: true
                    });
                } else if (response == "empty") {
                    swal({
                        title: "¡Un segundo!",
                        text: "Debes seleccionar algún interes.",
                        customClass: 'default-div',
                        timer: 4000,
                        showConfirmButton: true
                    });
                }
            },
            error: function (rs, e) {
                alert('Error');
            }
        });
        return false;
    });

    // Add follow
    $('.card-action').on('click', '.follow-user', function () {
        var slug = $(this).data('user-id');
        AJAX_requestfriend(slug, 'noabort');
    });
    // Exist follow request
    $('.card-action').on('click', '.follow_request', function () {
        var slug = $(this).data('user-id');
        AJAX_remove_request_friend(slug);
    });
    // Remove block relation
    $('.card-action').on('click', '.unblock-user', function () {
        var slug = $(this).data('user-id');
        AJAX_remove_bloq(slug);
    });
});

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/*PETICION AJAX PARA AGREGAR AMIGO*/
function AJAX_requestfriend(slug, status) {
    console.log('REQUEST FRIEND');
    if (status == "noabort") {
        $.ajax({
            type: "POST",
            url: "/request_friend/",
            data: {
                'slug': slug,
                'csrfmiddlewaretoken': csrftoken
            },
            dataType: "json",
            success: function (response) {
                if (response == "isfriend") {
                    swal({
                        title: "¡Ya es tu amigo!",
                        type: "warning",
                        customClass: 'default-div',
                        animation: "slide-from-top",
                        showConfirmButton: true,
                        showCancelButton: true,
                        confirmButtonColor: "#DD6B55",
                        confirmButtonText: "Unfollow",
                        cancelButtonText: "Ok, fine!",
                        closeOnConfirm: true
                    },
                        function (isConfirm) {
                            if (isConfirm) {
                                AJAX_remove_relationship(slug);
                            }
                        });
                } else if (response == "inprogress") {
                    var _btn = $('.card-action').find("[data-user-id='" + slug + "']");
                    $(_btn).replaceWith('<button data-user-id=' + slug + ' class="btn waves-effect waves-light blue darken-1 follow_request" type="submit">' + 'Solicitud enviada' + '</button>');
                } else if (response == "user_blocked") {
                    swal({
                        title: "Petición denegada.",
                        text: "El usuario te ha bloqueado.",
                        customClass: 'default-div',
                        type: "error",
                        timer: 4000,
                        animation: "slide-from-top",
                        showConfirmButton: false
                    });
                } else if (response == "added_friend") {
                    var _btn = $('.card-action').find("[data-user-id='" + slug + "']");
                    $(_btn).replaceWith('<button data-user-id=' + slug + ' class="btn waves-effect waves-light blue darken-1 follow-user" type="submit">' + 'Dejar de seguir' + '</button>');
                }
                else {

                }
            },
            error: function (rs, e) {
                alert(rs.responseText + " " + e);
            }
        });
    } else if (status == "anonymous") {
        alert("Debe estar registrado");
    }
}

/* Eliminar relacion entre dos usuarios */
function AJAX_remove_relationship(slug) {
    $.ajax({
        type: 'POST',
        url: '/remove_relationship/',
        data: {
            'slug': slug,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (response) {
            if (response == true) {
                var addFriendButton = $('.card-action').find("[data-user-id='" + slug + "']");
                $(addFriendButton).replaceWith('<button data-user-id=' + slug + ' class="btn waves-effect waves-light blue darken-1 follow-user" type="submit">' + 'Seguir' + '</button>');
            } else if (response == false) {
                swal({
                    title: "¡Ups!",
                    text: "Ha surgido un error, inténtalo de nuevo más tarde :-(",
                    customClass: 'default-div'
                });
            }
        }, error: function (rs, e) {

        }
    });
}

/* Eliminar peticion de amistad */
function AJAX_remove_request_friend(slug) {
    $.ajax({
        type: 'POST',
        url: '/remove_request_follow/',
        data: {
            'slug': slug,
            'status': 'cancel',
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (response) {
            if (response == true) {
                var addFriendButton = $('.card-action').find("[data-user-id='" + slug + "']");
                $(addFriendButton).replaceWith('<button data-user-id=' + slug + ' class="btn waves-effect waves-light blue darken-1 follow-user" type="submit">' + 'Seguir' + '</button>');
            } else if (response == false) {
                swal({
                    title: "¡Ups!",
                    text: "Ha surgido un error, inténtalo de nuevo más tarde.",
                    customClass: 'default-div'
                });
            }
        }, error: function (rs, e) {

        }
    });
}
/* Eliminar bloqueo al usuario */
function AJAX_remove_bloq(slug) {
    $.ajax({
        type: 'POST',
        url: '/remove_blocked/',
        data: {
            'slug': slug,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (response) {
            if (response == true) {
                var addFriendButton = $('.card-action').find("[data-user-id='" + slug + "']");
                $(addFriendButton).replaceWith('<button data-user-id=' + slug + ' class="btn waves-effect waves-light blue darken-1 follow-user" type="submit">' + 'Seguir' + '</button>');
            } else {
                swal({
                    title: "Tenemos un problema...",
                    customClass: 'default-div',
                    text: "Hubo un problema con su petición.",
                    timer: 4000,
                    showConfirmButton: true
                });
            }
        }, error: function (rs, e) {
            // alert(rs.responseText + " " + e);
        }
    });
}