;(function ($) {
    var chipsHandleEvents = false;
    var materialChipsDefaults = {
        data: [],
        placeholder: '',
        secondaryPlaceholder: '',
    };

    $(document).ready(function () {
        // Handle removal of static chips.
        $(document).on('click', '.chip .close', function (e) {
            var $chips = $(this).closest('.chips');
            if ($chips.data('initialized')) {
                return;
            }
            $(this).closest('.chip').remove();
        });
    });

    $.fn.material_chip = function (options) {
        var self = this;
        this.$el = $(this);
        this.$document = $(document);
        this.SELS = {
            CHIPS: '.chips',
            CHIP: '.chip',
            INPUT: 'input',
            DELETE: '.material-icons',
            SELECTED_CHIP: '.selected',
        };

        if ('data' === options) {
            return this.$el.data('chips');
        }

        if ('options' === options) {
            return this.$el.data('options');
        }

        this.$el.data('options', $.extend({}, materialChipsDefaults, options));

        // Initialize
        this.init = function () {
            var i = 0;
            var chips;
            self.$el.each(function () {
                var $chips = $(this);
                if ($chips.data('initialized')) {
                    // Prevent double initialization.
                    return;
                }
                var options = $chips.data('options');
                if (!options.data || !options.data instanceof Array) {
                    options.data = [];
                }
                $chips.data('chips', options.data);
                $chips.data('index', i);
                $chips.data('initialized', true);

                if (!$chips.hasClass(self.SELS.CHIPS)) {
                    $chips.addClass('chips');
                }

                self.chips($chips);
                i++;
            });
        };

        this.handleEvents = function () {
            var SELS = self.SELS;

            self.$document.on('click', SELS.CHIPS, function (e) {
                $(e.target).find(SELS.INPUT).focus();
            });

            self.$document.on('click', SELS.CHIP, function (e) {
                $(SELS.CHIP).removeClass('selected');
                $(this).toggleClass('selected');
            });

            self.$document.on('keydown', function (e) {
                if ($(e.target).is('input, textarea')) {
                    return;
                }

                // delete
                var $chip = self.$document.find(SELS.CHIP + SELS.SELECTED_CHIP);
                var $chips = $chip.closest(SELS.CHIPS);
                var length = $chip.siblings(SELS.CHIP).length;
                var index;

                if (!$chip.length) {
                    return;
                }

                if (e.which === 8 || e.which === 46) {
                    e.preventDefault();
                    var chipsIndex = $chips.data('index');

                    index = $chip.index();
                    self.deleteChip(chipsIndex, index, $chips);

                    var selectIndex = null;
                    if ((index + 1) < length) {
                        selectIndex = index;
                    } else if (index === length || (index + 1) === length) {
                        selectIndex = length - 1;
                    }

                    if (selectIndex < 0) selectIndex = null;

                    if (null !== selectIndex) {
                        self.selectChip(chipsIndex, selectIndex, $chips);
                    }
                    if (!length) $chips.find('input').focus();

                    // left
                } else if (e.which === 37) {
                    index = $chip.index() - 1;
                    if (index < 0) {
                        return;
                    }
                    $(SELS.CHIP).removeClass('selected');
                    self.selectChip($chips.data('index'), index, $chips);

                    // right
                } else if (e.which === 39) {
                    index = $chip.index() + 1;
                    $(SELS.CHIP).removeClass('selected');
                    if (index > length) {
                        $chips.find('input').focus();
                        return;
                    }
                    self.selectChip($chips.data('index'), index, $chips);
                }
            });

            self.$document.on('focusin', SELS.CHIPS + ' ' + SELS.INPUT, function (e) {
                $(e.target).closest(SELS.CHIPS).addClass('focus');
                $(SELS.CHIP).removeClass('selected');
            });

            self.$document.on('focusout', SELS.CHIPS + ' ' + SELS.INPUT, function (e) {
                $(e.target).closest(SELS.CHIPS).removeClass('focus');
            });

            self.$document.on('keydown', SELS.CHIPS + ' ' + SELS.INPUT, function (e) {
                var $target = $(e.target);
                var $chips = $target.closest(SELS.CHIPS);
                var chipsIndex = $chips.data('index');
                var chipsLength = $chips.children(SELS.CHIP).length;

                // comma
                //NOTE: modified
                if (188 === e.which) {
                    e.preventDefault();
                    self.addChip(chipsIndex, {tag: $target.val()}, $chips);
                    $target.val('');
                    return;
                }

                // delete or left
                if ((8 === e.keyCode || 37 === e.keyCode) && '' === $target.val() && chipsLength) {
                    self.selectChip(chipsIndex, chipsLength - 1, $chips);
                    $target.blur();
                    return;
                }
            });

            self.$document.on('click', SELS.CHIPS + ' ' + SELS.DELETE, function (e) {
                var $target = $(e.target);
                var $chips = $target.closest(SELS.CHIPS);
                var $chip = $target.closest(SELS.CHIP);
                e.stopPropagation();
                self.deleteChip(
                    $chips.data('index'),
                    $chip.index(),
                    $chips
                );
                $chips.find('input').focus();
            });

            // add chips on click
            self.$document.on('click', '.top-theme', function (e) {
                var $target = $(e.target);
                var $chips = $('.chips');
                var chipsIndex = $chips.data('index');
                e.stopPropagation();
                self.addChip(chipsIndex, {tag: $target.text().trim()}, $chips);

            });
        };

        this.chips = function ($chips) {
            var html = '';
            var options = $chips.data('options');
            $chips.data('chips').forEach(function (elem) {
                html += self.renderChip(elem);
            });
            html += '<input class="input" placeholder="">';
            $chips.html(html);
            self.setPlaceholder($chips);
        };

        this.renderChip = function (elem) {
            if (!elem.tag) return;
            var html = '<div class="chip">' + elem.tag;
            if (elem.image) {
                html += ' <img src="' + elem.image + '"> ';
            }
            html += '<i class="material-icons close">close</i>';
            html += '</div>';
            return html;
        };

        this.setPlaceholder = function ($chips) {
            var options = $chips.data('options');
            if ($chips.data('chips').length && options.placeholder) {
                $chips.find('input').prop('placeholder', options.placeholder);
            } else if (!$chips.data('chips').length && options.secondaryPlaceholder) {
                $chips.find('input').prop('placeholder', options.secondaryPlaceholder);
            }
        };

        this.isValid = function ($chips, elem) {
            var chips = $chips.data('chips');
            var exists = false;
            for (var i = 0; i < chips.length; i++) {
                if (chips[i].tag === elem.tag) {
                    exists = true;
                    return;
                }
            }
            if (!(/\S/.test(elem.tag))) {
                return false;
            }
            return '' !== elem.tag && !exists;
        };

        this.addChip = function (chipsIndex, elem, $chips) {
            if (!self.isValid($chips, elem)) {
                return;
            }
            var options = $chips.data('options');
            var chipHtml = self.renderChip(elem);
            $chips.data('chips').push(elem);
            $(chipHtml).insertBefore($chips.find('input'));
            $chips.trigger('chip.add', elem);
            self.setPlaceholder($chips);

        };

        this.deleteChip = function (chipsIndex, chipIndex, $chips) {
            var chip = $chips.data('chips')[chipIndex];
            $chips.find('.chip').eq(chipIndex).remove();
            $chips.data('chips').splice(chipIndex, 1);
            $chips.trigger('chip.delete', chip);
            self.setPlaceholder($chips);
        };

        this.selectChip = function (chipsIndex, chipIndex, $chips) {
            var $chip = $chips.find('.chip').eq(chipIndex);
            if ($chip && false === $chip.hasClass('selected')) {
                $chip.addClass('selected');
                $chips.trigger('chip.select', $chips.data('chips')[chipIndex]);
            }
        };

        this.getChipsElement = function (index, $chips) {
            return $chips.eq(index);
        };

        // init
        this.init();

        if (!chipsHandleEvents) {
            this.handleEvents();
            chipsHandleEvents = true;
        }
    };
}(jQuery));

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