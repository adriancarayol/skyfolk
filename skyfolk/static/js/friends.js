
$(document).ready(function(){
	/*
	addProfileCard("pepe");
	addProfileCard("juan");
	addProfileCard("eufrasio");
	addProfileCard("condemor");
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



function addProfileCard(username){

	$("#content_profile_cards").append('<div class="profile_card"><div class="header"><div class="inner_head"><a href="#"><span class="entypo-plus"></span><i>Agregar</i></a><a href="#"><span class="entypo-chat"></span><i>Chat</i></a><a href="#"><span class="entypo-star"></span><i>Favorito</i></a><a href="#"><span class="entypo-heart-empty"></span><i>Me gusta</i></a></div></div><div class="perfil"><div class="foto_perfil"></div><div class="inner_content"><h2 class="nomb" id="nomb">' + username + '</h2><span id="desc"><p class="descripcion" id="desc_one">Profunder</p><p class="descripcion" id="desc_two">Mensaje de texto de prueba </p></span><div class="social_links"><ul><li ><a id="Enviar..." href="/" class="button"><span class="entypo-forward"></span></a></li><li ><a id="Notificar..." href="/"  class="button"><span class="entypo-bell"></span></a></li> <li ><a id="Bloquear..." href="/"  class="button"><span class="entypo-block"></span></a></li> </ul></div></div></div></div>');


}


/*PETICION AJAX PARA CARGAR + AMIGOS*/
    function AJAX_loadFriends(){

                $.ajax({
                        type: "POST",
                        url: "/load_friends/",
                        data: {'slug': 4, 'csrfmiddlewaretoken': csrftoken},
                        dataType: "json",
                        success: function(response) {
                          
                        	//load friends
                        	//alert(response);
                        	/*
                        	response = JSON.parse(response)
                        	for (i=0;i<response.length;x++){
        						addProfileCard(response[i].user.username);

							}
							*/

                        },
                        error: function(rs, e) {
                           //alert(rs.responseText);
                           /*
                         	response = JSON.parse(response)
                        	for (i=0;i<response.length;x++){
        						addProfileCard(response[i].user.username);

							}
							*/                     
                        }
                });            

      
    }    
