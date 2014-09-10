$(document).ready(function(){
   $(".fontawesome-remove").click(function () {
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