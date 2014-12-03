
/*
$("#ilike_profile").click(function () {
    alert("ok!");
});
*/

	

    
var countFriendList = 1;
var countPublicationsList = 1;
		
    $(document).ready( function() {

    	$(".comment").shorten({
    		"showChars" : 145
    	});
    	
        $('#page-wrapper #close').on('click', function(event){
        	
        	$('#page-wrapper').hide();
            
        });
    	
        $('#publish').on('click', function(event){
        	
        	$(".entypo-mail").click();
            
        });
    	
    	
        $('#message-form2').on('submit', function(event){
        	
            event.preventDefault();
            AJAX_submit_publication();
            
        });
        
		$('#page-wrapper #message2').keypress(function(event){
			
			//tecla ENTER presinada
		    if(event.keyCode == 13){

			        $('#sendformpubli').click();

		    }
		});
        
        $('#tab-amigos').bind('scroll', function() {
            if($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {

            	countFriendList++;
                $.ajax({
                    type: "POST",
                    url: "/load_friends/",
                    data: {'slug': countFriendList, 'csrfmiddlewaretoken': csrftoken},
                    dataType: "json",
                    success: function(response) {
                      
                    	//load friends
                    	for (i=0;i<response.length;i++){
    						addFriendToHtmlList(response[i]);
						}
                    },
                    error: function(rs, e) {
						                   
                    }
                });
            	
            }
        });
        
        $('#tab-comentarios').bind('scroll', function() {
        	
            if($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight -10) {
    
            	countPublicationsList++;
                $.ajax({
                    type: "POST",
                    url: "/load_publications/",
                    data: {'slug': countPublicationsList, 'csrfmiddlewaretoken': csrftoken},
                    dataType: "json",
                    success: function(response) {
                    	//load publications
                    	for (i=0;i<response.length;i++){
                    		addPublicationToHtmlList(response[i]);
						}
                    	//refresca plugin shorten
                    	$(".comment").shorten({
                    		"showChars" : 145
                    	});
                    },
                    error: function(rs, e) {
						                   
                    }
                });
            	
            }
        });     
        
        
        $("#li-tab-amigos").click(function(){
            $('#tab-amigos').css({"overflow":"auto"});
        });
        
        $("#li-tab-comentarios").click(function(){
            $('#tab-comentarios').css({"overflow":"auto"});

        });
        
        $("#li-tab-popular").click(function(){
            $('#tab-popular').css({"overflow":"auto"});
        });
        
    	

    
      $('#tab-container').easytabs({

    	  defaultTab: "#li-tab-comentarios",
    	  animate: false

      });
      
      
      
    });

function addFriendToHtmlList(item){
	$("#tab-amigos ul.list-friends").append('<li><img src="' + STATIC_URL + 'img/generic-avatar.png" class="img-responsive"><a href="/profile/' + item.user__username + '">' + item.user__first_name + ' ' + item.user__last_name + ' (' + item.user__username + ')</a></li>');
	
} 
    
function addPublicationToHtmlList(item){
	
	$("#tab-comentarios").append('<div class="wrapper">\
			  <div id="box">\
		        <input id="profile" type="checkbox" checked>\
		        <label class="popo" for="profile">\
		        <img id="avatar-publication" src="' + STATIC_URL + 'img/generic-avatar.png" alt="img" class="img-responsive">\
		        </label>\
		        <span class="entypo-thumbs-up" title="¡Me gusta!"></span>\
		        <span class="entypo-forward" title="Responder"></span>\
		    <span class="entypo-plus" title="Añadir a..."></span>\
		  </div>\
		  <article class="articulo">\
		    <h2 class="h22"><a href="/profile/' + item.user__username + '" >' + item.user__username + '</a> mentioned you</h2>\
		    <div class="parrafo comment">\
		      <a target="_blank">' + item.from_publication__created + '</a> ' + item.from_publication__content + '\
		    </div>\
		  </article>\
	</div>');
	
}




    
    
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




    function AJAX_submit_publication(){
   
            //event.preventDefault(); //stop submit
            $.ajax({
                url: '/publication/',
                type: 'POST',
                dataType: 'json',
                data: $('#page-wrapper #message-form2').serialize(),
                success: function(data) {
                	if (data == true){
                		alert("You have successfully posted!");
                		$('#page-wrapper').hide();
                	}
                	else{
                		alert("Failed to publish");
                	}
                	
                },
                error: function(rs, e) {
                    alert('ERROR: ' + rs.responseText);
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

                                alert("Ya es amigo tuyo");                                              
                                                            
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
   $(".nameact").click(function () {
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

function addItemToFriendList(name, lastname){
	
	$("#tab-amigos ul").append('<li><img src="{{STATIC_URL}}img/generic-avatar.png" class="img-responsive"><a>' + name + ' ' + lastname + '</a></li>');
	
}


$(document).ready(function(){

    

});


/* NEW FLOT */ 

    var items = document.querySelectorAll('.circle a');

for(var i = 0, l = items.length; i < l; i++) {
  items[i].style.left = (20 - 30*Math.cos(-0.5 * Math.PI - 2*(1/l)*i*Math.PI)).toFixed(4) + "%";
  
  items[i].style.top = (35 + 35*Math.sin(-0.5 * Math.PI - 2*(1/l)*i*Math.PI)).toFixed(4) + "%";
}

document.querySelector('.profile').onclick = function(e) {
   e.preventDefault(); document.querySelector('.circle').classList.toggle('open');
}