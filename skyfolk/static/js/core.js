var keyPressTimeout;
$(window).ready(function () {
    $("#loader").fadeOut("slow");

});

$(document).ready(function () {
    var page_wrapper = $('#page-wrapper');
    var self_page_wrapper = $('#self-page-wrapper');
    var _group_profile = $('#group-profile');

    $('select').material_select();

    $('textarea#message2, textarea#message3').characterCounter();


    $(".button-menu-left").sideNav({
        edge: 'left', // Choose the horizontal origin
        menuWidth: 300,
        draggable: true
    });

    $(".button-right-notify").sideNav({
        edge: 'right', // Choose the horizontal origin
        menuWidth: 340,
        dragable: true
    });

    /* Mensaje flotante (perfil ajeno) */
    // #compose-new-no-comments
    $("#publish, #compose-new-no-comments").click(function () {
        $(page_wrapper).each(function () {
            var displaying = $(this).css("display");
            $(page_wrapper).find("#message3").val('');
            if (displaying == "none") {
                $(this).fadeOut('slow', function () {
                    $(this).css("display", "block");
                });
                $(this).find('#message3').focus();
            } else {
                $(this).find('#message3').blur();
                $(this).fadeIn('slow', function () {
                    $(this).css("display", "none");
                });
            }
        });
    });
    /* Mensaje flotante (perfil propio) */
    $("#publish2, #publish3, #compose-self-new-no-comments").click(function () {
        $(self_page_wrapper).each(function () {
            var displaying = $(this).css("display");
            $(self_page_wrapper).find("#message2").val('');
            if (displaying == "none") {
                $(this).fadeOut('slow', function () {
                    $(this).css("display", "block");
                });
                $(this).find('#message2').focus();
            } else {
                $(this).find('#message2').blur();
                $(this).fadeIn('slow', function () {
                    $(this).css("display", "none");
                });
            }
        });
    });

    /* Crear nuevo grupo de usuarios */

    $("#new_group").click(function () {
        $('#create_group').toggle();
    });

    /* Close nuevo grupo */
    $("#btn_close_group").click(function () {
        $('#create_group').hide();
    });

    /* Close page-wrapper (mensaje) */
    $(page_wrapper).find('#close').on('click', function (event) {
        event.preventDefault();
        $(page_wrapper).find('#message3').val('');
        $(page_wrapper).hide();
    });
    /* Close self-page-wrapper (mensaje propio) */
    $(self_page_wrapper).find('#close').on('click', function (event) {
        event.preventDefault();
        $(self_page_wrapper).find('#message2').val('');
        $(self_page_wrapper).hide();
    });

    /* Submit publication */
    $(page_wrapper).find('#message-form2').on('submit', function (event) {
        event.preventDefault();
        var data = $(page_wrapper).find('#message-form2').serialize();

        AJAX_submit_publication(data, 'publication');
    });

    /* Submit publication (propio) */
    $(self_page_wrapper).find('#message-form2').on('submit', function (event) {
        event.preventDefault();
        var data = $(self_page_wrapper).find('#message-form2').serialize();
        AJAX_submit_publication(data, 'publication');
    });

    /* Submit reply publication º*/
    $('button.enviar').on('click', function (event) {
        event.preventDefault();
        var parent_pk = $(this).attr('id').split('-')[1];
        var form = $(this).parent();
        $(form).find('input[name=parent]').val(parent_pk);
        var user_pk = $(form).find('input[name=author]').val();
        var owner_pk = $(form).find('input[name=board_owner]').val();
        var data = $(form).serialize();
        var pks = [user_pk, owner_pk, parent_pk];
        AJAX_submit_publication(data, 'reply', pks);
    });

    /* Submit creacion de grupo */
    $('button#btn_new_group').on('click', function (event) {
        event.preventDefault();
        var form = $(this).closest('#from_new_group');
        var owner_pk = $(form).find('input[name=owner]').val();
        console.log(owner_pk);
        var data = $(form).serialize();
        AJAX_submit_group(data);
    });
    /**** ATAJOS DE TECLADO ****/

    /* Mostrar atajos */
    $('#atajos-keyboard-profile').find('.atajos-title .fa-close').on('click', function () {
        $('#atajos-keyboard-profile').hide();
    });

    /* Atajo para enviar comentarios mas rapido */
    $(page_wrapper).find('#message3').keypress(function (e) {
        //tecla ENTER presinada + Shift
        if ((e.ctrlKey || e.metaKey) && (e.keyCode == 13 || e.keyCode == 10) && $(this).is(":visible")) {
            $('#sendformpubli').click();
            $(this).val(''); // CLEAR TEXTAREA
            $(this).blur(); // OFF FOCUS
        }
    });
    /* Atajo para enviar comentarios mas rapido a mi perfil. */
    $(self_page_wrapper).find('#message2').keypress(function (e) {
        //tecla ENTER presinada + Shift
        if ((e.ctrlKey || e.metaKey) && (e.keyCode == 13 || e.keyCode == 10) && $(this).is(":visible")) {
            $('#sendselfformpubli').click();
            $(this).val(''); // CLEAR TEXTAREA
            $(this).blur(); // OFF FOCUS
        }
    });

    /* Abrir - Cerrar lista de atajos */
    $('#vertical-menu').find('.shortcut-keyboard').on('click', function () {
        $('#atajos-keyboard-profile').toggle();
    });


    /* Abre nuevo mensaje "m" */
    $(this).keypress(function (e) {
        var key = e.keyCode || e.which;
        if (key == 109 && ($(page_wrapper).is(':hidden')) && !($('input').is(":focus")) && !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
            // Si presionas el char 'm' mostará el div para escribir un mensaje.
            $(page_wrapper).toggle();
            $(page_wrapper).find('#message3').focus();
            return false;
        }
    });
    /* Abre nuevo mensaje (propio) "m" */
    $(this).keypress(function (e) {
        var key = e.keyCode || e.which;
        if (key == 77 && ($(self_page_wrapper).is(':hidden')) && !($('input').is(":focus")) && !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
            // Si presionas el char 'm' mostará el div para escribir un mensaje.
            $(self_page_wrapper).toggle();
            $(self_page_wrapper).find('#message2').focus();
            return false;
        }
    });

    /* Abre atajos "a" */
    $(this).keypress(function (e) {
        var key = e.keyCode || e.which;
        var cheat = document.getElementById('atajos-keyboard-profile');
        if (key == 97 && ($(cheat).is(':hidden')) && !($('input').is(":focus")) && !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
            // Si presionas el char 'm' mostará el div para escribir un mensaje.
            $(cheat).show();
        }
    });

    /* Cierra todas las ventajas emergentes/menus. */
    $(this).on('keydown', function (e) {
        var key = e.keyCode || e.which;
        if (key === 27) { // escape
            var ampliado = document.getElementsByClassName('ampliado');
            var atj = document.getElementById('atajos-keyboard-profile');
            var personalInfo = document.getElementsByClassName('info-paw');
            var searchInput = document.getElementById('id_searchText');
            var messageWrapperMessage3 = $(page_wrapper).find('#message3');
            var messageWrapperMessage2 = $(self_page_wrapper).find('#message2');

            $(messageWrapperMessage2).blur(); // Focus del textarea off.
            $(messageWrapperMessage2).val("");
            $(page_wrapper).hide();  // Oculta form para crear comentario.
            $(messageWrapperMessage3).blur(); // Focus del textarea off.
            $(messageWrapperMessage3).val("");
            $(self_page_wrapper).hide(); // Oculta form para crear comentario.
            $(atj).hide(); // Oculta atajos de teclado.
            $(ampliado).hide(); // Oculta mensaje ampliado.
            $(personalInfo).hide(); // Oculta informacion personal
            $("#create_group").hide(); // Oculta form para crear grupo
            $(searchInput).val("");
            $(searchInput).blur();
            /* OCULTAR MENUS VERTICALES (NOTIFICACION Y MENU USUARIO */
            $('.side-nav').sideNav('hide');
        }
    });
    /* Focus on input search */
    $(this).on('keydown', function (e) {
        if (e.keyCode === 111 && ($('#atajos-keyboard-profile').is(':hidden')) && !($('input').is(":focus")) && !($('textarea').is(":focus"))) { // escape
            $('#id_searchText').focus(); // Focus del textarea off.
            return false;
        }
    });

    /* Marcar todas las notificaciones como leidas */
    $('#clear-notify').on('click', function () {
        AJAX_mark_all_read();
    });

    /* Agregar Amigo por medio de PIN */
    $('#agregar-amigo, #agregar-amigo2').on('click', function () {
        swal({
            title: "Add new friend!",
            customClass: "default-div",
            text: "Insert the friend's username or PIN",
            type: "input",
            animation: "slide-from-top",
            showConfirmButton: true,
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Add it!",
            cancelButtonText: "Cancel!",
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function (inputValue) {
            if (inputValue === false) return false;
            if (inputValue === "") {
                swal.showInputError("You need to write something!");
                return false
            }
            AJAX_addNewFriendByUsernameOrPin(inputValue);
        });
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

    // Search users
    $('#id_searchText').on("keydown", function (event) {
        clearTimeout(keyPressTimeout);
        keyPressTimeout = setTimeout(function () {
                var data = {
                    'value': $('#id_searchText').val()
                };
                $.ajax({
                    url: '/pre_search/users/',
                    type: "GET",
                    dataType: "json",
                    data: data,
                    success: function (result) {
                        $('#id_searchText').atwho({
                            at: '',
                            searchKey: "username",
                            insertTpl: "${username}",
                            displayTpl: "<li data-value='(${username}, ${username})'><img src='${avatar}' width='30px' height='30px'> ${username} <small>${first_name} ${last_name}</small></li>",
                            data: result.result,
                            limit: 20,
                            callback: {
                                filter: function (query, data, search_key) {
                                    return $.map(data, function (item, i) {
                                        return item[search_key].toLowerCase().indexOf(query) < 0 ? null : item
                                    })
                                }
                            }
                        });
                    }
                });
            },
            250
        );
    });
}); // END DOCUMENT READY

/* COMPLEMENTARIO PARA PETICIONES AJAX */
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
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

/* FUNCIONES PARA NOTIFICACIONES */

/* Para marcar las publicaciones de un usuario como leidas */
function AJAX_mark_all_read() {
    $.ajax({
        url: '/inbox/notifications/mark-all-as-read/',
        data: {
            'csrfmiddlewaretoken': csrftoken
        },
        type: 'POST',
        success: function () {
            $('#notification-menu').find('li').fadeOut("fast");
            $("#live_notify_badge").html(0);
        },
        error: function (rs, e) {
            alert('ERROR: ' + rs.responseText + e);
        }
    });
}
/* Para marcar una notificacion como leida */
function AJAX_mark_read(obj) {
    var slug = obj.getAttribute('data-notification');
    var url_ = '/inbox/notifications/mark-as-read/' + slug + '/';
    $.ajax({
        url: url_,
        data: {
            'csrfmiddlewaretoken': csrftoken
        },
        type: 'POST',
        success: function () {
            $(obj).parent().fadeOut("fast");
            var currentValue = document.getElementById('live_notify_badge');
            if (parseInt($(currentValue).html()) > 0)
                $(currentValue).html(parseInt($(currentValue).html()) - 1);
        },
        error: function (rs, e) {
            alert('ERROR: ' + rs.responseText + e);
        }
    });
}
/* Para eliminar una notificacion */
function AJAX_delete_notification(slug, id) {
    var url_ = '/inbox/notifications/delete/' + slug + '/';
    $.ajax({
        url: url_,
        data: {
            'csrfmiddlewaretoken': csrftoken
        },
        type: 'POST',
        success: function () {
            $("ul.list-notifications").find("[data-id='" + id + "']").each(function () {
                $(this).hide();
            });
            var currentValue = document.getElementById('live_notify_badge');
            if (parseInt($(currentValue).html()) > 0)
                $(currentValue).html(parseInt($(currentValue).html()) - 1);
        },
        error: function (rs, e) {

        }
    });
}

function AJAX_addNewFriendByUsernameOrPin(valor) {
    $.ajax({
        type: "POST",
        url: "/add_friend_by_pin/",
        data: {
            'valor': valor,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (data) {
            console.log(data);
            var response = data.response;

            if (response == "added_friend") {
                swal({
                    title: "Success!",
                    text: "You have added a friend!",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                }, function () {
                    $('#addfriend').replaceWith('<span class="fa fa-remove" id="addfriend" title="Dejar de seguir" style="color: #29b203;" onclick=AJAX_requestfriend("noabort");>' + ' ' + '</span>');
                    if (data.friend_username)
                        addItemToFriendList(data.friend_first_name, data.friend_last_name, data.friend_username, data.friend_avatar);
                });
            } else if (response == 'your_own_pin') {
                swal({
                    title: "Wait a moment!",
                    text: "It's your own pin!",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response == 'your_own_username') {
                swal({
                    title: "Wait a moment!",
                    text: "It's your own username!",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response == 'its_your_friend') {
                swal({
                    title: "Wait a moment!",
                    text: "It's already your friend!",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response == 'its_blocked') {
                swal({
                    title: "Espera un momento!",
                    text: "Tienes bloqueado este perfil!",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response == 'no_added_friend') {
                swal({
                    title: "We have a problem",
                    text: "Friend no added",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response == 'no_match') {
                swal({
                    title: "We have a problem",
                    text: "This username or pin no exists.",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response == 'in_progress') {
                swal({
                    title: "Request in progress",
                    text: "Your request is to confirm!.",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response == 'new_petition') {
                swal({
                    title: "New petition sent!",
                    text: "Wait to confirm!.",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response == 'user_blocked') {
                swal({
                    title: "Petición denegada.",
                    text: "El usuario te ha bloqueado.",
                    customClass: 'default-div',
                    type: "error",
                    timer: 4000,
                    animation: "slide-from-top",
                    showConfirmButton: false
                });
            } else if (response == 'blocked_profile') {
                swal({
                    title: "Petición denegada.",
                    text: "Tienes bloqueado a este perfil.",
                    customClass: 'default-div',
                    type: "error",
                    timer: 4000,
                    animation: "slide-from-top",
                    showConfirmButton: false
                });
            }
        },
        error: function (rs, e) {
            alert(rs.responseText + " " + e);
        }
    });


}


function AJAX_respondFriendRequest(id_emitter, status, obj_data) {
    $.ajax({
        type: "POST",
        url: "/respond_friend_request/",
        data: {
            'slug': parseInt(id_emitter),
            'status': status,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (response) {
            if (response == "added_friend") {
                addItemToFriendList('Nuevo', 'nuevo');
                sweetAlert("You have added a friend!");
                $('li[data-id=' + obj_data + ']').fadeOut("fast");
            } else {
                $('li[data-id=' + obj_data + ']').fadeOut("fast");
            }
        },
        error: function (rs, e) {
            alert(rs.responseText + " " + e);
        }
    });


}

/*
 function addNewPublication(type, user_pk, board_owner_pk, parent) {
 if (type == "reply") {
 console.log(type + " " + user_pk + " " + board_owner_pk + " " + parent);
 $.get("/publication/list/?type=reply&user_pk=" + user_pk + "&board_owner_pk" + board_owner_pk + ",parent=" + parent, function (data) {
 console.log(data);
 $("#tab-comentarios").prepend(data).fadeIn('slow/400/fast');
 })
 } else {
 $.get("/publication/list/", function (data) {
 if ($("#tab-comentarios").find(".no-comments").length) {
 $("#tab-comentarios").find(".no-comments").remove()
 }
 $("#tab-comentarios").prepend(data).fadeIn('slow/400/fast')
 })
 }
 }
 */

function AJAX_submit_publication(data, type, pks) {
    type = typeof type !== 'undefined' ? type : "reply"; //default para type
    $.ajax({
        url: '/publication/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            var response = data.response;
            console.log('RESPONSE AQUI: ' + response + " type: " + type);
            if (response == true) {
                /* nothing */
            } else {
                swal({
                    title: "",
                    text: "Failed to publish",
                    customClass: 'default-div',
                    type: "error"
                });
            }
            if (type == "reply") {
                var caja_comentarios = $('#caja-comentario-' + pks[2]);
                $(caja_comentarios).find('#message-reply').val(''); // Borramos contenido
                $(caja_comentarios).fadeOut();
            } else if (type == "publication") {
                $('#page-wrapper, #self-page-wrapper').fadeOut("fast"); // Ocultamos el DIV al publicar un mensaje.
            }
        },
        error: function (rs, e) {
            swal({
                title: '¡Ups!',
                text: 'Revisa el contenido de tu mensaje', // rs.responseText,
                customClass: 'default-div',
                type: "error"
            });
        }
    }).done(function () {
        // No necesario, ya que usamos sockets para añadir
        // En "vivo" publicaciones y respuestas
        //addNewPublication(type, pks[0], pks[1], pks[2]);
    })
}


function AJAX_submit_group(data) {
    $.ajax({
        url: '/create_group/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function (data) {
            var response = data.response;
            console.log('RESPONSE AQUI (grupos): ' + response);
            if (response == true) {
                $('#create_group').hide();
            } else {
                swal({
                    title: "¡Ups!",
                    text: "Fallo al crear el grupo.",
                    customClass: 'default-div',
                    type: "error"
                });
            }
        },
        error: function (rs, e) {
            swal({
                title: '¡Ups!',
                text: 'Revisa el contenido de tu grupo.', // rs.responseText,
                customClass: 'default-div',
                type: "error"
            });
        }
    }).done(function () {

    })
}


/*PETICION AJAX PARA AGREGAR AMIGO*/
function AJAX_requestfriend(status) {
    var slug = $("#profileId").html();
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
            // swal(rs.responseText + " " + e);
        }
    });
}

/* Eliminar peticion de amistad */
function AJAX_remove_request_friend() {
    var slug = $("#profileId").html();
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
            // swal(rs.responseText + " " + e);
        }
    });
}

function AJAX_remove_bloq_from_config(obj) {
    var userid = $(obj).data('id');
    $.ajax({
        type: 'POST',
        url: '/remove_blocked/',
        data: {
            'slug': userid,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (response) {
            if (response == true) {
                $("ul").find("[data-id='" + userid + "']").hide();
            } else {
                swal({
                    title: "Tenemos un problema...",
                    text: "Hubo un problema con su petición.",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            }
        }, error: function (rs, e) {
            alert(rs.responseText + " " + e);
        }
    });
}
/*****************************************************/
/**********              UTIL                *********/
/*****************************************************/

function is_numeric(value) {
    var is_number = /^\d+$/.test(value);
    return is_number;
}

function serializedToJSON(data) {
    //from -> http://stackoverflow.com/questions/23287067/converting-serialized-forms-data-to-json-object
    data = data.split("&");
    var obj = {};
    for (var key in data) {
        obj[data[key].split("=")[0]] = data[key].split("=")[1]
    }

    return obj
}
