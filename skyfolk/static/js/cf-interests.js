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
                if (13 === e.which) {
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
                var needDelete = $target.hasClass('interest');
                var $chips = $('.chips');
                var chipsIndex = $chips.data('index');
                e.stopPropagation();
                self.addChip(chipsIndex, {tag: $target.text().trim(), delete: needDelete}, $chips);

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
            var tag = elem.tag.toLowerCase();
            if (elem.delete) {
                var html = '<div class="chip delete">' + tag;
            } else {
                var html = '<div class="chip">' + tag;
            }
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
                if (chips[i].tag.toLowerCase() === elem.tag.toLowerCase()) {
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
        secondaryPlaceholder: 'Música, Cine...'
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
            url: "/config/interests/",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'tags[]': text_tag,
                'choices[]': myCheckboxes
            },
            cache: false,
            dataType: "json",
            success: function (response) {
                if (response === "success") {
                    Materialize.toast('¡Intereses actualizados con éxito!', 4000);
                } else if (response === "with_spaces") {
                    swal({
                        title: "¡Un segundo!",
                        text: "Un interés no puede contener sólo espacios en blanco.",
                        customClass: 'default-div',
                        timer: 4000,
                        showConfirmButton: true
                    });
                } else if (response === "empty") {
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
});