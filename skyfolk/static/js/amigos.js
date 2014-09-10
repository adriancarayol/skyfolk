

/* abrir */
$(document).ready(function(){
   $(".fontawesome-plus").click(function () {
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
      $("#sectiom").each(function() {
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