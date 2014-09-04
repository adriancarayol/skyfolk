function closeMessage(el) {
  el.addClass('is-hidden');
}

$('.js-messageClose').on('click', function(e) {
  closeMessage($(this).closest('.Message'));
});

$(document).ready(function() {
  setTimeout(function() {
    closeMessage($('#js-timer'));
  }, 5000);
});


function closeMessage(el) {
  el.addClass('is-hidden');
}

$('a[target="x"]').on('click', function(e) {
  closeMessage($(this).closest('.love'));
});

$(document).ready(function() {
  setTimeout(function() {
    closeMessage($('.love'));
  }, 5000);
});

