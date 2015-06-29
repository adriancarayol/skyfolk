/*
$("#ilike_profile").click(function () {
    alert("ok!");
});
*/



var countFriendList = 1;
var countPublicationsList = 1;
var countTimeLine = 1;

$(document).ready(function() {

  $(".comment").shorten({
    "showChars": 145
  });

  $('#page-wrapper #close').on('click', function(event) {

    $('#page-wrapper').hide();

  });


  $('#publish').on('click', function(event) {

    $(".entypo-mail").click();

  });

  $('#publish2').on('click', function(event) {

    $(".entypo-mail").click();

  });

  $('.fa-paw').on('click',function() {
      $(".info-paw").fadeToggle("fast");
  });

  $('#message-form2').on('submit', function(event) {

    event.preventDefault();
    AJAX_submit_publication();

  });

  $('#page-wrapper #message2').keypress(function(event) {

    //tecla ENTER presinada
    if (event.keyCode == 13) {

      $('#sendformpubli').click();

    }
  });

  /* Abrir crear/cerrar grupo en search.html */

  $('.btn-floating').on('click',function(event) {
  	$('.crear-grupo').toggle("fast",function() {
  	});
  });

  $('#cerrar_grupo').on('click',function(event) {
  	$('.crear-grupo').hide();
  });


  $(document).keypress(function(e){
    var key = e.which;
    if (key == 109 && ($('#page-wrapper').is(':hidden'))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
        // Si presionas el char 'm' mostará el div para escribir un mensaje.
        $('#page-wrapper').toggle();
    }
  });


  $('#tab-amigos').bind('scroll', function() {
    if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight) {

      countFriendList++;
      $.ajax({
        type: "POST",
        url: "/load_friends/",
        data: {
          'slug': countFriendList,
          'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function(response) {

          //load friends
          for (i = 0; i < response.length; i++) {
            addFriendToHtmlList(response[i]);
          }
        },
        error: function(rs, e) {

        }
      });

    }
  });

  $('#tab-comentarios').bind('scroll', function() {

    if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight - 10) {

      countTimeLine++;
      $.ajax({
        type: "POST",
        url: "/load_publications/",
        data: {
          'slug': countTimeLine,
          'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function(response) {
          //load publications
          for (i = 0; i < response.length; i++) {
            addPublicationToHtmlList(response[i]);
          }
          //refresca plugin shorten
          $(".comment").shorten({
            "showChars": 145
          });
        },
        error: function(rs, e) {

        }
      });

    }
  });

$('#tab-timeline').bind('scroll', function() {

        if ($(this).scrollTop() + $(this).innerHeight() >= $(this)[0].scrollHeight - 10) {

            countPublicationsList++;
            $.ajax({
                type: "POST",
                url: "/load_publications/",
                data: {
                    'slug': countPublicationsList,
                    'csrfmiddlewaretoken': csrftoken
                },
                dataType: "json",
                success: function(response) {
                    //load publications
                    for (i = 0; i < response.length; i++) {
                        addPublicationToHtmlList(response[i]);
                    }
                    //refresca plugin shorten
                    $(".comment").shorten({
                        "showChars": 145
                    });
                },
                error: function(rs, e) {

                }
            });

        }
    });


  $("#li-tab-amigos").click(function() {
    $('#tab-amigos').css({
      "overflow": "auto"
    });
  });

  $("#li-tab-comentarios").click(function() {
    $('#tab-comentarios').css({
      "overflow": "auto"
    });

  });

  $("#li-tab-timeline").click(function() {
    $('#tab-popular').css({
      "overflow": "auto"
    });
  });



  $('#tab-container').easytabs({

    defaultTab: "#li-tab-comentarios",
    animate: false

  });



});

function addFriendToHtmlList(item) {

  if (item.user__profile__image) {
    $("#tab-amigos ul.list-friends").append('<li id="friend-' + item.user__id + '"><img src="' + MEDIA_URL + item.user__profile__image + '"  class="friend-avatar img-responsive"><a href="/profile/' + item.user__username + '">' + item.user__first_name + ' ' + item.user__last_name + ' (' + item.user__username + ')</a></li>');

    //SI NO EXISTE LA URL DE LA IMAGEN, SE CAMBIA POR EL AVATAR POR DEFECTO. QUITAR ESTO CUANDO
    //SE PUEDAN SUBIR IMAGENES SIN QUE DESAPAREZCAN MAS TARDE
    imageselector = $("#tab-amigos ul.list-friends #friend-" + item.user__id + " img.friend-avatar")
    URL_CHECK = MEDIA_URL + item.user__profile__image;
    URL_CHANGE = STATIC_URL + 'img/generic-avatar.png';
    //Check image URL;
    (function(imageselector, URL_CHECK, URL_CHANGE) {

      $.ajax({
        url: URL_CHECK,
        type: 'HEAD',
        data: {
          'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        error: function() {
          //url not exists
          //wait secs

          setTimeout(function() {

            //forma chula1
            imageselector.fadeOut("slow", function() {
              imageselector.attr("src", URL_CHANGE);
            });
            imageselector.fadeIn("slow");

          }, 750);

        }

      });

    })(imageselector, URL_CHECK, URL_CHANGE);

  } else {
    $("#tab-amigos ul.list-friends").append('<li id="friend-' + item.user__id + '"><img src="' + STATIC_URL + 'img/generic-avatar.png" class="friend-avatar img-responsive"><a href="/profile/' + item.user__username + '">' + item.user__first_name + ' ' + item.user__last_name + ' (' + item.user__username + ')</a></li>');
  }



}

function addPublicationToHtmlList(item) {

  if (item.user__profile__image) {
    $("#tab-comentarios").append('<div class="wrapper" id="pub-' + item.from_publication__id + '">\
			        <div id="box">\
			            <input id="profile" type="checkbox" checked>\
			            <label class="popo" for="profile">\
			            <img id="avatar-publication" src="' + MEDIA_URL + item.user__profile__image + '" alt="img" class="pub-avatar img-responsive">\
			            </label>\
			            <span class="entypo-thumbs-up" title="¡Me gusta!"></span>\
			            <span class="entypo-forward" title="Responder"></span>\
			        <span class="entypo-plus" title="Añadir a..."></span>\
			      </div>\
			      <article class="articulo">\
			        <h2 class="h22"><a href="/profile/' + item.user__username + '" >' + item.user__username + '</a> mentioned you</h2>\
			        <div class="parrafo comment">\
			          <a target="_blank">' + item.from_publication__created + '</a><br>' + item.from_publication__content + '\
			        </div>\
			      </article>\
			  </div>');



    //SI NO EXISTE LA URL DE LA IMAGEN, SE CAMBIA POR EL AVATAR POR DEFECTO. QUITAR ESTO CUANDO
    //SE PUEDAN SUBIR IMAGENES SIN QUE DESAPAREZCAN MAS TARDE
    imageselector = $("#tab-comentarios #pub-" + item.from_publication__id + " img.pub-avatar");
    URL_CHECK = MEDIA_URL + item.user__profile__image;
    URL_CHANGE = STATIC_URL + 'img/generic-avatar.png';
    //Check image URL
    (function(imageselector, URL_CHECK, URL_CHANGE) {

      $.ajax({
        url: URL_CHECK,
        type: 'HEAD',
        data: {
          'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        error: function() {

          setTimeout(function() {

            //forma chula1
            imageselector.fadeOut("slow", function() {
              imageselector.attr("src", URL_CHANGE);
            });
            imageselector.fadeIn("slow");

          }, 750);
        }
      });

    })(imageselector, URL_CHECK, URL_CHANGE);


  } else {
    $("#tab-comentarios").append('<div class="wrapper">\
			        <div id="box">\
			            <input id="profile" type="checkbox" checked>\
			            <label class="popo" for="profile">\
			            <img id="avatar-publication" src="' + STATIC_URL + 'img/generic-avatar.png" alt="img" class="pub-avatar img-responsive">\
			            </label>\
			            <span class="entypo-thumbs-up" title="¡Me gusta!"></span>\
			            <span class="entypo-forward" title="Responder"></span>\
			        <span class="entypo-plus" title="Añadir a..."></span>\
			      </div>\
			      <article class="articulo">\
			        <h2 class="h22"><a href="/profile/' + item.user__username + '" >' + item.user__username + '</a> mentioned you</h2>\
			        <div class="parrafo comment">\
			          <a target="_blank">' + item.from_publication__created + '</a><br>' + item.from_publication__content + '\
			        </div>\
			      </article>\
			  </div>');

  }



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
function AJAX_likeprofile(status) {
  //alert($("#likes strong").html());
  if (status == "noabort") {
    $.ajax({
      type: "POST",
      url: "/like_profile/",
      data: {
        'slug': $("#profileId").html(),
        'csrfmiddlewaretoken': csrftoken
      },
      //data: {'slug': $("#profileId").html()},
      dataType: "json",
      success: function(response) {

        if (response == "like") {

          $("#ilike_profile").css('color', '#29b203');

          //Aumentamos el valor del campo
          $("#likes strong").html(parseInt($("#likes strong").html()) + 1);

        } else if (response == "nolike") {

          $("#ilike_profile").css('color', '#46494c');

          if ($("#likes strong").html() > 0) {
            //Decrementar
            $("#likes strong").html(parseInt($("#likes strong").html()) - 1);
          }

        } else {

        }
      },
      error: function(rs, e) {
        alert(rs.responseText);
      }
    });
  } else if (status == "anonymous") {
    alert("Debe estar registrado");
  }

}


function AJAX_respondFriendRequest(id_emitter, status) {



  $.ajax({

    type: "POST",
    url: "/respond_friend_request/",
    data: {
      'slug': id_emitter,
      'status': status,
      'csrfmiddlewaretoken': csrftoken
    },
    dataType: "json",
    success: function(response) {

      if (response == "added_friend") {

        sweetAlert("You have added a friend!");


      } else {

      }
    },
    error: function(rs, e) {
      alert(rs.responseText);
    }
  });


}



function AJAX_submit_publication() {

  //event.preventDefault(); //stop submit
  $.ajax({
    url: '/publication/',
    type: 'POST',
    dataType: 'json',
    data: $('#page-wrapper #message-form2').serialize(),
    success: function(data) {
      if (data == true) {
        swal({
        	title: "",
        	text: "You have successfully posted!",
        	type: "success",
        	timer: 1000,
        	animation: "slide-from-top",
        	showConfirmButton: false,

        });
        $('#page-wrapper').hide();
      } else {
        swal({
        	title: "",
	        text: "Failed to publish",
		type: "error"
        });
      }

    },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText);
    }
  });


}



function showRequest(id_profile, username) {

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



$(document).ready(function() {
  //Examples of how to assign the ColorBox event to elements
  $(".inline").colorbox({
    inline: true,
    width: "78%"
  });
  $(".callbacks").colorbox({
    onOpen: function() {
      alert('onOpen: colorbox is about to open');
    },
    onLoad: function() {
      alert('onLoad: colorbox has started to load the targeted content');
    },
    onComplete: function() {
      alert('onComplete: colorbox has displayed the loaded content');
    },
    onCleanup: function() {
      alert('onCleanup: colorbox has begun the close process');
    },
    onClosed: function() {
      alert('onClosed: colorbox has completely closed');
    }
  });

  //Example of preserving a JavaScript event for inline calls.
  $("#click").click(function() {
    $('#click').css({
      "background-color": "#f00",
      "color": "#fff",
      "cursor": "inherit"
    }).text("Open this window again and this message will still be here.");
    return false;
  });
});



/*PETICION AJAX PARA AGREGAR AMIGO*/
function AJAX_requestfriend(status) {
    //alert($("#likes strong").html());

    if (status == "noabort") {
      $.ajax({
        type: "POST",
        url: "/request_friend/",
        data: {
          'slug': $("#profileId").html(),
          'csrfmiddlewaretoken': csrftoken
        },
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
          if (response == "isfriend") {

            alert("Ya es amigo tuyo");

          } else if (response == "inprogress") {

            //alert("peticion en curso");
            $('<img id = "friend_request_progress" src="../../static/img/friend_request_progress.png">').insertBefore(".caja");

          } else {

          }
        },
        error: function(rs, e) {
          alert(rs.responseText);
        }
      });
    } else if (status == "anonymous") {
      alert("Debe estar registrado");
    }



  }
  /* DISPLAY MENU */

$(document).ready(function() {
  $(".fa-bars").click(function() {
    $("#toggle").each(function() {
      displaying = $(this).css("display");
      $("#toggle").val('');
      if (displaying == "none") {
        $(this).fadeToggle(function() {
          $(this).css("display", "block");
        });
      } else {
        $(this).fadeToggle(function() {
          $(this).css("display", "none");
        });
      }
    });
  });
});
/* Mensaje flotante */
$(document).ready(function() {
  $(".entypo-mail").click(function() {
    $("#page-wrapper").each(function() {
      displaying = $(this).css("display");
      $("#page-wrapper #message2").val('');
      if (displaying == "none") {
        $(this).fadeOut('slow', function() {
          $(this).css("display", "block");
        });
      } else {
        $(this).fadeIn('slow', function() {
          $(this).css("display", "none");
        });
      }
    });
  });
});

/* DISPLAY MESSAGES */

$(document).ready(function() {
  $(".fa-bell").click(function() {
    $("#notificationn").each(function() {
      displaying = $(this).css("display");
      $("#notificationn").val('');
      if (displaying == "none") {
        $(this).fadeToggle(function() {
          $(this).css("display", "block");
        });
      } else {
        $(this).fadeToggle(function() {
          $(this).css("display", "none");
        });
      }
    });
  });
});;


function addItemToFriendList(name, lastname) {

  $("#tab-amigos ul").append('<li><img src="{{STATIC_URL}}img/generic-avatar.png" class="img-responsive"><a>' + name + ' ' + lastname + '</a></li>');

}


$(document).ready(function() {



});
