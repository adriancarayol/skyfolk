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
    $('.follow-user').click(function () {
        var slug = $(this).data('user-id');
        AJAX_requestfriend(slug, 'noabort');
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
    if (status == "noabort") {
        $.ajax({
            type: "POST",
            url: "/request_friend/",
            data: {
                'slug': slug,
                'csrfmiddlewaretoken': csrftoken
            },
            //data: {'slug': $("#profileId").html()},
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
                    $('#addfriend').replaceWith('<span class="fa fa-clock-o" id="follow_request" title="En proceso" onclick="AJAX_remove_request_friend();">' + ' ' + '</span>');
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
                    $('#addfriend').replaceWith('<span class="fa fa-remove" id="addfriend" title="Dejar de seguir" style="color: #29b203;" onclick=AJAX_requestfriend("noabort");>' + ' ' + '</span>');
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
                var currentValue = document.getElementById('followers-stats');
                var addFriendButton = document.getElementById('addfriend');
                $(currentValue).html(parseInt($(currentValue).html()) - 1);
                $(addFriendButton).replaceWith('<span id="addfriend" class="fa fa-plus" title="Seguir" style="color:#555 !important;" onclick=AJAX_requestfriend("noabort");>' + ' ' + '</span>');
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
                $('#follow_request').replaceWith('<span id="addfriend" class="fa fa-plus" title="Seguir" onclick=AJAX_requestfriend("noabort");></span>');
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