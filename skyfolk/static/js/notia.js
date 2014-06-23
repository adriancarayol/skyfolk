$(function() {
  $(".notifications .messages").hide();
  $(".notifications").click(function() {
    if ($(this).children(".messages").children().length > 0) {
      $(this).children(".messages").fadeToggle(300);
    }
  });
});