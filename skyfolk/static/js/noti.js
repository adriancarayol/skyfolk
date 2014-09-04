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