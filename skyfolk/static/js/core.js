var keyPressTimeout;

$(window).ready(function () {
    $("#loader").fadeOut("slow");

});

$(document).ready(function () {
    var page_wrapper = $('#page-wrapper');
    var self_page_wrapper = $('#self-page-wrapper');
    var tab_comentarios = $('#tab-comentarios');

    $('select').material_select();
    $('.materialboxed').materialbox();
    $('textarea#message2, textarea#message3').characterCounter();

    var Autocomplete = function (options
    ) {
        this.form_selector = options.form_selector;
        this.url = options.url || '/search/autocomplete/';
        this.delay = parseInt(options.delay || 300);
        this.minimum_length = parseInt(options.minimum_length || 3);
        this.form_elem = null;
        this.query_box = null;
    }

    Autocomplete.prototype.setup = function () {
        var self = this;

        this.form_elem = $(this.form_selector);
        this.query_box = this.form_elem.find('input[name=q]');

        // Watch the input box.
        this.query_box.on('keyup', function () {
            var query = self.query_box.val();

            if (query.length < self.minimum_length) {
                return false;
            }

            self.fetch(query);
        })
    }

    Autocomplete.prototype.fetch = function (query) {
        var self = this

        $.ajax({
            url: this.url
            , data: {
                'q': query
            }
            , success: function (data) {
                self.show_results(data);
            }
        })
    }

    Autocomplete.prototype.show_results = function (data) {
        // Remove any existing results.
        $('.ac-results').remove();

        var results = data.results || [];
        var results_wrapper = $('<div class="ac-results"></div>');
        var base_elem = $('<div class="result-wrapper"><a href="#" class="ac-result"></a></div>');

        if (results.length > 0) {
            for (var res_offset in results) {
                var elem = base_elem.clone();
                var result = elem.find('.ac-result');
                result.attr('href', '/profile/' + results[res_offset].username);
                result.text('@' + results[res_offset].username + ' (' + results[res_offset].first_name + ' ' +
                    results[res_offset].last_name + ')');
                result.prepend(results[res_offset].avatar);
                results_wrapper.append(elem);
            }
        }
        else {
            var elem = base_elem.clone()
            elem.text("No se encontraron resultados.");
            results_wrapper.append(elem);
        }

        this.query_box.after(results_wrapper);
    }
    window.autocomplete = new Autocomplete({
        form_selector: '.autocomplete-me'
    })

    window.autocomplete.setup();

    $(".button-menu-left").sideNav({
        edge: 'left', // Choose the horizontal origin
        menuWidth: 300,
        draggable: false
    });

    $(".button-right-notify").sideNav({
        edge: 'right', // Choose the horizontal origin
        menuWidth: 300,
        dragable: false
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
        return false;
    });

    /* Close page-wrapper (mensaje) */
    $(page_wrapper).find('.close').on('click', function (event) {
        event.preventDefault();
        $(page_wrapper).find('#message2').val('');
        $(page_wrapper).hide();
    });
    /* Close self-page-wrapper (mensaje propio) */
    $(self_page_wrapper).find('.close').on('click', function (event) {
        event.preventDefault();
        $(self_page_wrapper).find('#message3').val('');
        $(self_page_wrapper).hide();
    });

    /* Submit publication */
    $(page_wrapper).find('#message-form2').on('submit', function (event) {
        event.preventDefault();
        var form = $(page_wrapper).find('#message-form2');
        AJAX_submit_publication(form, 'publication');
    });

    /* Submit publication (propio) */
    $(self_page_wrapper).find('#message-form3').on('submit', function (event) {
        event.preventDefault();
        var form = $(self_page_wrapper).find('#message-form3');
        AJAX_submit_publication(form, 'publication');
    });

    /* Submit reply publication */
    $(tab_comentarios).on('click', 'button.enviar', function (event) {
        event.preventDefault();
        var parent_pk = $(this).attr('id').split('-')[1];
        var form = $(this).parent();
        AJAX_submit_publication(form, 'reply', parent_pk);
    });

    /* Submit creacion de grupo */
    $('button#btn_new_group').on('click', function (event) {
        event.preventDefault();
        AJAX_submit_group();
    });

    /**** ATAJOS DE TECLADO ****/

    /* Mostrar atajos */
    $('#atajos-keyboard-profile').find('.atajos-title .close-shortcuts').on('click', function () {
        $('#atajos-keyboard-profile').hide();
    });

    /* Submit new message */
    $(this).on('keypress', function (e) {
        var activeElement = document.activeElement;
        var form = $(activeElement).closest('form').first();
        if (form) {
            if ((e.ctrlKey || e.metaKey) && (e.keyCode === 13 || e.keyCode === 10)) {
                var submit = $(form).find(':submit');
                submit.click();
            }
        }
    });

    /* Abrir - Cerrar lista de atajos */
    $('#vertical-menu').find('.shortcut-keyboard').on('click', function () {
        $('#atajos-keyboard-profile').toggle();
    });


    /* Abre nuevo mensaje "m" */
    $(this).keypress(function (e) {
        var key = e.keyCode || e.which;
        if (key === 109 && ($(page_wrapper).is(':hidden')) && !($('input').is(":focus")) && !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
            // Si presionas el char 'm' mostará el div para escribir un mensaje.
            $(page_wrapper).toggle();
            $(page_wrapper).find('#message3').focus();
            return false;
        }
    });
    /* Abre nuevo mensaje (propio) "m" */
    $(this).keypress(function (e) {
        var key = e.keyCode || e.which;
        if (key === 77 && ($(self_page_wrapper).is(':hidden')) && !($('input').is(":focus")) && !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
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
        if (key === 65 && ($(cheat).is(':hidden')) && !($('input').is(":focus")) && !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
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
            $('.ac-results').remove(); // Elimina resultados sugeridos
            $(ampliado).hide(); // Oculta mensaje ampliado.
            $(personalInfo).hide(); // Oculta informacion personal
            $("#create_group").hide(); // Oculta form para crear grupo
            $(searchInput).val("");
            $(searchInput).blur();
            /* OCULTAR MENUS VERTICALES (NOTIFICACION Y MENU USUARIO */
            $('.side-nav').sideNav('hide');
        }
    });

    /* REMOVE suggestion results */
    $(this).click(function (event) {
        if (!$(event.target).closest('.ac-results').length) {
            $('.ac-results').remove();
        }
    });

    /* Focus on input search */
    $(this).on('keydown', function (e) {
        if (e.keyCode === 111 && ($('#atajos-keyboard-profile').is(':hidden')) && !($('input').is(":focus")) && !($('textarea').is(":focus"))) { // escape
            $('#id_q').focus(); // Focus del textarea off.
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
            title: "¡Sigue a un nuevo usuario!",
            customClass: "default-div",
            text: "Introduce su nombre de usuario",
            type: "input",
            animation: "slide-from-top",
            showConfirmButton: true,
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "¡Seguir!",
            cancelButtonText: "Cancelar",
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
                            displayTpl: "<li class='search-live-item' data-value='${username}'><img src='${avatar}' width='30px' height='30px'>${username} <small>${first_name} ${last_name}</small></li>",
                            data: result.result,
                            displayTimeout: 100,
                            callback: {
                                filter: function (query, data, searchKey) {
                                    return $.map(data, function (item, i) {
                                        if (item[searchKey].toLowerCase().indexOf(query) < 0 ||
                                            item['first_name'].toLowerCase().indexOf(query) < 0 ||
                                            item['last_name'].toLowerCase().indexOf(query) < 0) {
                                            return item;
                                        } else {
                                            return null;
                                        }
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
            $("#live_notify_badge").find('b').html(0);
        },
        error: function (rs, e) {
            alert('ERROR: ' + rs.responseText + e);
        }
    });
}

/* Para marcar una notificacion como leida */
function AJAX_mark_read(obj) {
    let slug = obj.getAttribute('data-notification');
    let url_ = '/inbox/notifications/mark-as-read/' + slug + '/';
    $.ajax({
        url: url_,
        data: {
            'csrfmiddlewaretoken': csrftoken
        },
        type: 'POST',
        success: function () {
            $(obj).parent().fadeOut("fast");
            let currentValue = $('#live_notify_badge').find('b');
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
            var currentValue = $('#live_notify_badge').find('b');
            if (parseInt($(currentValue).html()) > 0)
                $(currentValue).html(parseInt($(currentValue).html()) - 1)
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
            var response = data.response;

            if (response === "added_friend") {
                swal({
                    title: "¡Bien!",
                    text: "Ahora sigues a " + data.friend_username,
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                }, function () {
                    $('#addfriend').replaceWith('<li class="material-icons unfollow-profile" id="addfriend" title="Dejar de seguir" style="color: #29b203;" onclick=AJAX_requestfriend("noabort");>' + 'remove' + '</li>');
                    if (data.friend_username)
                        if (typeof addItemToFriendList === "function")
                            addItemToFriendList(data.friend_first_name, data.friend_last_name, data.friend_username, data.friend_avatar);
                });
            } else if (response === 'your_own_username') {
                swal({
                    title: "¡Espera un momento!",
                    text: "¿Estás intentando seguirte a ti mismo?",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response === 'its_your_friend') {
                swal({
                    title: "¡Espera un momento!",
                    text: "¡Ya lo sigues!",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response === 'its_blocked') {
                swal({
                    title: "Espera un momento!",
                    text: "¡Tienes bloqueado este perfil!",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response === 'no_added_friend') {
                swal({
                    title: "Tenemos un problema...",
                    text: "La petición ha fallado",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response === 'in_progress') {
                swal({
                    title: "Petición en progreso",
                    text: "¡Tu petición está a la espera de ser aceptada!",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response === 'new_petition') {
                swal({
                    title: "¡Petición enviada!",
                    text: "¡Ahora espera a que te acepte la invitación!",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
                });
            } else if (response === 'user_blocked') {
                swal({
                    title: "Petición denegada",
                    text: "El usuario te ha bloqueado",
                    customClass: 'default-div',
                    type: "error",
                    timer: 4000,
                    animation: "slide-from-top",
                    showConfirmButton: false
                });
            } else if (response === 'blocked_profile') {
                swal({
                    title: "Petición denegada",
                    text: "Tienes bloqueado a este perfil",
                    customClass: 'default-div',
                    type: "error",
                    timer: 4000,
                    animation: "slide-from-top",
                    showConfirmButton: false
                });
            } else {
                swal({
                    title: "Tenemos un problema...",
                    text: "Parece que no existe ningún usuario con ese nombre",
                    customClass: 'default-div',
                    timer: 4000,
                    showConfirmButton: true
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
            var currentValue = $('#live_notify_badge').find('b');
            if (parseInt($(currentValue).html()) > 0)
                $(currentValue).html(parseInt($(currentValue).html()) - 1)

            if (response == "added_friend") {
                sweetAlert("¡Has añadido un seguidor!");
                $('li[data-id=' + obj_data + ']').fadeOut("fast");
            } else {
                $('li[data-id=' + obj_data + ']').fadeOut("fast");
            }
        },
        error: function (rs, e) {
            // alert(rs.responseText + " " + e);
        }
    });


}

function AJAX_respondGroupRequest(id_object, status, obj_data) {
    $.ajax({
        type: "POST",
        url: "/respond_group_request/",
        data: {
            'slug': parseInt(id_object),
            'status': status,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (data) {
            var response = data.response;
            if (response == "added_friend") {
                sweetAlert("¡Has añadido un nuevo miembro al grupo!");
                $('li[data-id=' + obj_data + ']').fadeOut("fast");
            } else if (response == 'error') {
                swal({
                    title: "¡Ups!",
                    text: "Es posible que el usuario haya cancelado la solicitud.",
                    customClass: 'default-div',
                    type: "error"
                });
            } else {
                $('li[data-id=' + obj_data + ']').fadeOut("fast");
            }
        },
        error: function (rs, e) {
            // alert(rs.responseText + " " + e);
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

function AJAX_submit_publication(obj_form, type, pks) {
    var form = new FormData($(obj_form).get(0));
    form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    type = typeof type !== 'undefined' ? type : "reply"; //default para type
    $.ajax({
        url: '/publication/',
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
                $('#page-wrapper, #self-page-wrapper').fadeOut("fast"); // Ocultamos el DIV al publicar un mensaje.
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


function AJAX_submit_group() {
    var f = $('#from_new_group');
    var form = new FormData(f.get(0));
    form.append('csrfmiddlewaretoken', getCookie('csrftoken'));
    $.ajax({
        url: '/create_group/',
        type: 'POST',
        dataType: 'json',
        contentType: false,
        processData: false,
        async: true,
        enctype: 'multipart/form-data',
        data: form,
        success: function (data) {
            var msg = data.msg;
            var group_created = data.group_created;
            if (typeof(msg) !== 'undefined' && msg !== null) {
                Materialize.toast(msg, 4000);
            }
            if (typeof data.pk !== 'undefined' && data.pk !== null) {
                f.trigger("reset");
                var wrapper_groups_row = $('.wrapper-groups').find('.row').first();
                $(wrapper_groups_row).prepend(group_created);
                $('#create_group').hide();
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
    if (status === "noabort") {
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
                if (response === "isfriend") {
                    swal({
                            title: "¡Ya es tu amigo!",
                            type: "warning",
                            customClass: 'default-div',
                            animation: "slide-from-top",
                            showConfirmButton: true,
                            showCancelButton: true,
                            confirmButtonColor: "#DD6B55",
                            confirmButtonText: "Dejar de seguir",
                            cancelButtonText: "¡Ah, vale!",
                            closeOnConfirm: true
                        },
                        function (isConfirm) {
                            if (isConfirm) {
                                AJAX_remove_relationship(slug);
                            }
                        });
                } else if (response === "inprogress") {
                    $('#addfriend').replaceWith('<li class="material-icons cancel-request" id="follow_request" title="En proceso" onclick="AJAX_remove_request_friend();">' + 'watch_later' + '</li>');
                } else if (response === "user_blocked") {
                    swal({
                        title: "Petición denegada.",
                        text: "El usuario te ha bloqueado.",
                        customClass: 'default-div',
                        type: "error",
                        timer: 4000,
                        animation: "slide-from-top",
                        showConfirmButton: false
                    });
                } else if (response === "added_friend") {
                    var currentValue = document.getElementById('followers-stats');
                    $(currentValue).html(parseInt($(currentValue).html()) + 1);
                    $('#addfriend').replaceWith('<li class="material-icons unfollow-profile" id="addfriend" title="Dejar de seguir" style="color: #29b203;" onclick=AJAX_requestfriend("noabort");>' + 'remove' + '</li>');
                }
                else {

                }
            },
            error: function (rs, e) {
                alert(rs.responseText + " " + e);
            }
        });
    } else if (status === "anonymous") {
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
                $(addFriendButton).replaceWith('<li id="addfriend" class="material-icons follow-profile" title="Seguir" style="color:#555 !important;" onclick=AJAX_requestfriend("noabort");>' + 'add' + '</li>');
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
                $('#follow_request').replaceWith('<span id="addfriend" class="material-icons follow-profile" title="Seguir" onclick=AJAX_requestfriend("noabort");>' + 'add' + '</li>');
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
