

/* abrir */
$(document).ready(function(){
   $(".new-post, .live").click(function () {
      $("#section").each(function() {
        displaying = $(this).css("display");
        if(displaying == "none") {
          $(this).fadeOut('slow',function() {
           $(this).css("display","block");
          });
        } else {
          $(this).fadeIn('slow',function() {
            $(this).css("display","none");
          });
        }
      });
    });
  });
/* cerrar */ 
$(document).ready(function(){
   $(".fontawesome-remove").click(function () {
      $("#section").each(function() {
        displaying = $(this).css("display");
        if(displaying == "block") {
          $(this).fadeOut('slow',function() {
           $(this).css("display","none");
          });
        } else {
          $(this).fadeIn('slow',function() {
            $(this).css("display","none");
          });
        }
      });
    });
  });



/* VARIABLES PARA HACER APARECER BOTONES */

jQuery(document).ready(function($) {
  var iconPencil = $('.controls .new-post .icon-pencil');
  var iconPlus = $('.controls .new-post .icon-plus');
  var liveBtn = $('.controls .live') 
  var liveBtn2 = $('.controls .live2');
  var newPostBtn = $('.controls .new-post');
  $('.controls').hover(function() {
    $(iconPencil).addClass('active');
    $(iconPlus).addClass('unactive');
    $(liveBtn).addClass('active');
    $(liveBtn2).addClass('active');
  }, function() {
    $(iconPencil).removeClass('active');
    $(iconPlus).removeClass('unactive');
    $(liveBtn).removeClass('active');
    $(liveBtn2).removeClass('active')
  });
});
