$(document).ready(function(){
   $("#Menu").click(function () {
      $("#panel").each(function() {
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
/*
$("#ilike_profile").click(function () {
    alert("ok!");
});
*/

});

/* COMPLEMENTARIO PARA PETICIONES AJAX */
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
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

/*PETICION AJAX PARA 'I LIKE' DEL PERFIL*/
    function AJAX_likeprofile(status){
              //alert($("#likes strong").html());
              if (status == "noabort"){
                  $.ajax({
                        type: "POST",
                        url: "/like_profile/",
                        data: {'slug': $("#profileId").html(), 'csrfmiddlewaretoken': csrftoken},
                        //data: {'slug': $("#profileId").html()},
                        dataType: "json",
                        success: function(response) {
                          
                           if (response == "like"){

                                $("#ilike_profile").css('color', '#29b203');
                                                 
                                //Aumentamos el valor del campo
                                $("#likes strong").html(parseInt($("#likes strong").html()) + 1);
                                                            
                           }else if(response == "nolike"){

                                $("#ilike_profile").css('color', '#46494c');

                                if ($("#likes strong").html() > 0){
                                      //Decrementar
                                      $("#likes strong").html(parseInt($("#likes strong").html()) - 1);
                                }                                
                                                      
                           }else{
                                
                           }
                        },
                        error: function(rs, e) {
                           alert(rs.responseText);
                        }
                  });            
              }else if (status == "anonymous"){
                  alert("Debe estar registrado");
              }
      
    }

$(document).ready(function(){
   $(".nameact").click(function () {
      $("#menu").each(function() {
        displaying = $(this).css("display");
        if(displaying == "block") {
          $(this).fadeOut('slow',function() {
           $(this).css("display","none");
          });
        } else {
          $(this).fadeIn('slow',function() {
            $(this).css("display","block");
          });
        }
      });
    });
  });



function aparecerbola(){
  document.getElementById("widget").style.opacity = "1";
  document.getElementById("widget").style.webkitTransition = "opacity 1s linear";
}
/*
function cambiopagina(){
  document.getElementById("linkedin").style.opacity = "1";
  document.getElementById("linkedin").style.webkitTransition = "opacity 0.9s linear";
  setTimeout('location.href="/friends"', 500);
}
function cambiopagina(){
  document.getElementById("twitter").style.opacity = "1";
  document.getElementById("twitter").style.webkitTransition = "opacity 0.9s linear";
  setTimeout('location.href="/outsession"', 500);
}

*/





      $(document).ready(function(){
        //Examples of how to assign the ColorBox event to elements
                $(".inline").colorbox({inline:true, width:"78%"});
        $(".callbacks").colorbox({
          onOpen:function(){ alert('onOpen: colorbox is about to open'); },
          onLoad:function(){ alert('onLoad: colorbox has started to load the targeted content'); },
          onComplete:function(){ alert('onComplete: colorbox has displayed the loaded content'); },
          onCleanup:function(){ alert('onCleanup: colorbox has begun the close process'); },
          onClosed:function(){ alert('onClosed: colorbox has completely closed'); }
        });
        
        //Example of preserving a JavaScript event for inline calls.
        $("#click").click(function(){ 
          $('#click').css({"background-color":"#f00", "color":"#fff", "cursor":"inherit"}).text("Open this window again and this message will still be here.");
          return false;
        });
      });
      
      
      
      
      
      
$(document).ready(function(){
   $(".nameact").click(function () {
      $("#panel1").each(function() {
        displaying = $(this).css("display");
        if(displaying == "block") {
          $(this).fadeOut('slow',function() {
           $(this).css("display","none");
          });
        } else {
          $(this).fadeIn('slow',function() {
            $(this).css("display","block");
          });
        }
      });
    });
  });

/* Mensaje flotante */
$(document).ready(function(){
   $(".entypo-mail").click(function () {
      $("#page-wrapper").each(function() {
        displaying = $(this).css("display");
        if(displaying == "block") {
          $(this).fadeOut('slow',function() {
           $(this).css("display","none");
          });
        } else {
          $(this).fadeIn('slow',function() {
            $(this).css("display","block");
          });
        }
      });
    });
  });
