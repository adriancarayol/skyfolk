
/*
$("#ilike_profile").click(function () {
    alert("ok!");
});
*/

    $(document).ready( function() {
      $('#tab-container').easytabs({
    	  /*
    	  transitionOut: "hide",
    	  animationSpeed: 0,
    	  transitionCollapse: "hide",
    	  transitionUncollapse: "show",
    	  animationSpeed: 0
    	  */
    	  defaultTab: "#li-tab-comentarios"
    	  
    	  

      });
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


    function AJAX_respondFriendRequest(id_emitter, status){
             
              
                   
                  $.ajax({
                     
                        type: "POST",
                        url: "/respond_friend_request/",
                        data: {'slug': id_emitter, 'status': status, 'csrfmiddlewaretoken': csrftoken},
                        dataType: "json",
                        success: function(response) {
                          
                           if (response == "added_friend"){

                              alert("You have added a friend!");
                                                             
                                                      
                           }else{
                                
                           }
                        },
                        error: function(rs, e) {
                           alert(rs.responseText);
                        }
                  });
                     
      
    }



function aparecerbola(){
  document.getElementById("widget").style.opacity = "1";
  document.getElementById("widget").style.webkitTransition = "opacity 1s linear";
}

function showRequest(id_profile, username){

        var unique_id = $.gritter.add({
          // (string | mandatory) the heading of the notification
          title: username + ' wants to be your friend!',
          // (string | mandatory) the text inside the notification
          text: '',
          // (string | optional) the image to display on the left
          image: '../../static/img/imagesgritter/a.png',
          // (bool | optional) if you want it to fade out on its own or just sit there
          sticky: true,
          // (int | optional) the time you want it to be alive for before fading out
          time: '',
          // (string | optional) the class name you want to apply to that specific message
          class_name: 'gritter-light',
          
          //new options
          button1: true,
          button2: true,
          height: "85px",
          type: "friendrequest",
          buttons_function: AJAX_respondFriendRequest,
          id_emitter: id_profile,

        });  

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
      
      
      
/*PETICION AJAX PARA AGREGAR AMIGO*/
    function AJAX_requestfriend(status){
              //alert($("#likes strong").html());
           
              if (status == "noabort"){
                  $.ajax({
                        type: "POST",
                        url: "/request_friend/",
                        data: {'slug': $("#profileId").html(), 'csrfmiddlewaretoken': csrftoken},
                        //data: {'slug': $("#profileId").html()},
                        dataType: "json",
                        success: function(response) {
                          /*
                           if (response == "friend"){

                                $("#addfriend").css('color', '#29b203');                                                
                                                            
                           }else if(response == "nofriend"){

                                $("#addfriend").css('color', '#46494c');                              
                                                      
                           }else{
                                
                           }
                           */
                           if (response == "isfriend"){

                                alert("ya es amigo tuyo");                                              
                                                            
                           }else if(response == "inprogress"){

                                //alert("peticion en curso");
                                $( '<img id = "friend_request_progress" src="../../static/img/friend_request_progress.png">' ).insertBefore( ".caja" );                            
                                                      
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
      
 /* MENU AL PULSAR FOTO DE USUARIO */     
$(document).ready(function(){
   $(".nameact").mouseenter(function () {
      $("#panel1").each(function() {
        displaying = $(this).css("display");
        if(displaying == "none") {
          $(this).fadeOut(250 ,function() {
           $(this).css("display","block");
          });
        } else {
          $(this).fadeIn(250 ,function() {
            $(this).css("display","none");
          });
        }
      });
    });
  });

/* CERRAR MENU AL QUITAR EL CURSOR DE ENCIMA */
$(document).ready(function(){
   $("#panel1").mouseleave(function () {
      $("#panel1").each(function() {
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

/* Mensaje flotante */
$(document).ready(function(){
   $(".entypo-mail").click(function () {
      $("#page-wrapper").each(function() {
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
/* Configuración rápida */
$(document).ready(function(){
   $(".fontawesome-pencil").click(function () {
      $("#fastconf").each(function() {
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

$(document).ready(function(){
   $(".fontawesome-remove").click(function () {
      $("#fastconf").each(function() {
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


function addItemToFriendList(name, lastname){
	
	$("#tab-amigos ul").append('<li><img src="{{STATIC_URL}}img/generic-avatar.png" class="img-responsive"><a>' + name + ' ' + lastname + '</a></li>');
	
}


$(document).ready(function(){

    

});