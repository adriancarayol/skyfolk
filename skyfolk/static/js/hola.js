
(function() {
  var $body, $value, restore;

  $('[data-hide]').on('click', function() {
    var $message, $this;

    $this = $(this);
    $message = $this.parent();
    restore($message);
    return $message.addClass('hide');
  });

  $('[data-close]').on('click', function() {
    var $message, $this;

    $this = $(this);
    $message = $this.parent();
    restore($message);
    return $message.addClass('hide');
  });

  restore = function(el) {
    return el.one('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend', function() {
      return setTimeout((function() {
        return el.removeClass('hide');
      }), 1000);
    });
  };

  $body = $('body');

  $value = $('#font-size-value');

  $('#font-size').on('change', function() {
    var value;

    value = this.value;
    $value.html( + value + em);
    return $body.css('font-size',  + value + em);
  });

}).call(this);