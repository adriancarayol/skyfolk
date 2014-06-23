$(document).ready(function () {
  $(".fontawesome-bell-alt").click(function () {
    $(this).toggleClass("open");
    $("#notificationMenu").toggleClass("open");
  });
});