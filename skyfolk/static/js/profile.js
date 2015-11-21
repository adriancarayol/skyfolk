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

  /* LOADER para el perfil */
  /*
  $(window).load(function(e) {
    $('.logotipo_skyfolk').addClass('logotipo_skyfolk-1');
    $('body').css('background-color','tomato');
  }); 

*/
/*

  $('#publish').on('click', function(event) {

    $(".fa-paper-plane").click();

  });

  $('#publish2').on('click', function(event) {

    $(".fa-paper-plane").click();

  });
*/
  
  /* Al hacer click en el menu "bola" avanzamos hacia el TOP de la pagina */
/*
  $('.profile').click(function(){
    $("html, body").animate({ scrollTop: 0 }, 200);
    return false;
 });
*/
  $('.fa-paw').on('click',function() {
      $(".info-paw").fadeToggle("fast");
  });

  $('.info-trof').on('click',function() {
    $(".trofeos").fadeToggle("fast");
  });

  $('.info-groups').on('click',function() {
    $(".grupos").fadeToggle("fast");
  });

  $('#close-trofeos').on('click',function() {
    $(".trofeos").fadeOut("fast");
  });

  $('#close-grupos').on('click',function() {
     $(".grupos").fadeOut("fast");
  });

  $('#message-form2').on('submit', function(event) {

    event.preventDefault();
    AJAX_submit_publication();

  });

  $('#atajos-keyboard-profile .atajos-title .fa-close').on('click',function() {
    $('#atajos-keyboard-profile').fadeOut();
  });


  /* Menu vertical al hacer click cambia el estilo de "fa-bars" */
/*
  $(document).ready(function() {
    $('.fa-bars').on('click',function() {
          $(this).toggleClass("fa-bars-rotate");
        });
  });
*/

    /* Borrar publicacion */
  $('.optiones_comentarios .fa-trash').on('click',function() {
    var caja_publicacion = $(this).closest('.wrapper');
    //alert($(caja_comentario).html());
    swal({
        	title: "Are you sure?",
            text: "You will not be able to recover this publication!",
            type: "warning",
        	animation: "slide-from-top",
        	showConfirmButton: true,
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Yes, delete it!",
            cancelButtonText: "No God, please no!",
            closeOnConfirm: true
        }, function(isConfirm) {
            if (isConfirm) {
                AJAX_delete_publication(caja_publicacion);
            }
        });
  });

    /* Agregar timeline */
    $('.optiones_comentarios .fa-tag').on('click', function() {
        var caja_publicacion = $(this).closest('.wrapper');
        alert('VAS A AÑADIR EL COMENTARIO A TU TIMELINE');
        AJAX_add_timeline(caja_publicacion);
    });

    /* Añadir me gusta a comentario */
    $('.optiones_comentarios .fa-heart').on('click', function() {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this
        AJAX_add_like(caja_publicacion, heart);
    })

/* Mostramos y ocultamos notificaciones y chat por la derecha */

  $(".fa-bell").click(function(){
            ($(".nav-vertical-and-chat").animate({width: 'toggle'},100) && $('body').toggleClass('move-body'));
        });


  /* Atajo para enviar comentarios mas rapido */

  $('#page-wrapper #message2').keypress(function(event) {
    //tecla ENTER presinada + Shift
    if (event.keyCode == 13 && event.shiftKey) {

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

  /* Abrir - Cerrar lista de atajos */

  $('.menup li:nth-child(7)').on('click',function() {
    $('#atajos-keyboard-profile').fadeToggle("fast");
  });

/* ATAJOS DE DECLADO */

/* Abre nuevo mensaje "m" */

  $(document).keypress(function(e){
    var key = e.which;
    if (key == 109 && ($('#page-wrapper').is(':hidden')) && 
    !$('.search-in-tab').is(":focus") && 
    !($('#id_searchText').is(":focus")) && 
    !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
        // Si presionas el char 'm' mostará el div para escribir un mensaje.
        $('#page-wrapper').toggle();
    }
  });
/* Abre atajos "a" */

$(document).keypress(function(e){
    var key = e.which;
    if (key == 97 && ($('#atajos-keyboard-profile').is(':hidden')) && 
    !$('.search-in-tab').is(":focus") && 
    !($('#id_searchText').is(":focus")) && 
    !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
        // Si presionas el char 'm' mostará el div para escribir un mensaje.
        $('#atajos-keyboard-profile').show();
    }
});

/* Cierra todas las ventajas emergentes. */

$( document ).on('keydown', function(e) {
    if ( e.keyCode === 27 && 
    ($('#atajos-keyboard-profile').is(':visible') ||
    $('#page-wrapper').is(':visible'))) { // escape
        
        $('#page-wrapper').hide();
        $('#atajos-keyboard-profile').hide();

    }
});

  /* FUNCIONES AJAX PARA TABS DE PERFIL */
  
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
          // $('#tab-comentarios').load(location.href + " #tab-comentarios");
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
/*
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

/**/
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
    $('#tab-timeline').css({
      "overflow": "auto"
    });
  });



  $('#tab-container').easytabs({

        defaultTab: "#li-tab-comentarios",
        animate: true,
        animationSpeed: "fast",
        updateHash: false,


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
                  <input type="checkbox" id="check-' + item.from_publication__id +'">\
                  <label for="check-' + item.from_publication__id +'" class="zoom-pub"><i class="fa fa-expand fa-lg"></i></label>\
                  <div class="image">\
                  <img id="avatar-publication" src="' + STATIC_URL + 'img/generic-avatar.png" alt="img" class="usr-img img-responsive">\
                  </div>\
            </div>\
            <article class="articulo">\
              <h2 class="h22"><a href="/profile/' + item.user__username + '" >' + item.user__username + '</a> mentioned you</h2>\
              <div class="parrafo comment">\
                <a target="_blank">' + item.from_publication__created + '</a><br><br>' + item.from_publication__content + '\
              </div>\
              <div class="optiones_comentarios">\
                <ul class="opciones">\
                       <li><i class="fa fa-heart"></i></li>\
                       <li><i class="fa fa-quote-left"></i></li>\
                       <li><i class="fa fa-reply"></i></li>\
                       <li><i class="fa fa-tag"></i></li>\
                    </ul>\
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
        
      } else {
        swal({
          title: "",
          text: "Failed to publish",
    type: "error"
        });
      }
      
        $('#page-wrapper').hide(); // Ocultamos el DIV al publicar un mensaje.
        
        /* EN PRUEBAS */
        var html = $(data).filter('#tab-comentarios').html();

        $('#tab-comentarios').load(location.href + " #tab-comentarios"); // Mediante AJAX actualizamos los comentarios cuando hay uno nuevo.

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
  $(".fa-bars").on("click", function(event) {
    if ( !$(event.target).is( "li" )) {

    $("#toggle").each(function() {
      displaying = $(this).css("display");
      $("#toggle").val('');
      if (displaying == "none") {
        $(this).fadeToggle('fast',function() {
          $(".fa-bars").addClass('fa-bars-rotate'); // Cambiamos el color de "fa-bars" para saber que el menu vertical está abierto.
          $(this).css("display", "block");
        });
      } else {
        $(this).fadeToggle('fast',function() {
          $(".fa-bars").removeClass('fa-bars-rotate'); // Si esta oculto, fa-bars estará en su estado normal.
          $(this).css("display", "none");
        });
      }
    });
      }
  });
});

/* Mensaje flotante */
$(document).ready(function() {
  $("#publish2").click(function()  {
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

$(document).ready(function() {
  $("#publish").click(function()  {
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


function addItemToFriendList(name, lastname) {

  $("#tab-amigos ul").append('<li><img src="{{STATIC_URL}}img/generic-avatar.png" class="img-responsive"><a>' + name + ' ' + lastname + '</a></li>');

}

/*****************************************************/
/********** AJAX para botones de comentarios *********/
/*****************************************************/

function AJAX_delete_publication(caja_publicacion) {
  var id_pub = $(caja_publicacion).attr('id').split('-')[1]  // obtengo id
  var id_user = $(caja_publicacion).data('id')// obtengo id
  var data = {
           userprofile_id: id_user,
           publication_id: id_pub
       };
  //event.preventDefault(); //stop submit
  $.ajax({
    url: '/publication/delete/',
    type: 'POST',
    dataType: 'json',
    data: data,
    success: function(data) {
        // borrar caja publicacion
        if (data==true) {
            $(caja_publicacion).fadeToggle("fast");
        }else{
            swal({
                title: "Fail",
                text: "Failed to delete publish.",
                type: "error"
            });
        }
    },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText);
    }
  });


}

/*****************************************************/
/********** AJAX para añadir me gusta a comentario *********/
/*****************************************************/

function AJAX_add_like(caja_publicacion, heart) {
  var id_pub = $(caja_publicacion).attr('id').split('-')[1]  // obtengo id
  var id_user = $(caja_publicacion).data('id')// obtengo id
  var data = {
           userprofile_id: id_user,
           publication_id: id_pub
       };
  //event.preventDefault(); //stop submit
  $.ajax({
    url: '/publication/add_like/',
    type: 'POST',
    dataType: 'json',
    data: data,
    success: function(data) {
        if (data==true) {
            $(heart).css('color','#f06292');
        }else{
            swal({
                title: "Fail",
                text: "Failed to add like.",
                type: "error"
            });
        }
    },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText);
    }
  });


}

/*****************************************************/
/********** AJAX para agregar al TIMELINE *********/
/*****************************************************/

function AJAX_add_timeline(caja_publicacion) {
  var id_pub = $(caja_publicacion).attr('id').split('-')[1]  // obtengo id
  var id_user = $(caja_publicacion).data('id')// obtengo id
  var data = {
           userprofile_id: id_user,
           publication_id: id_pub
       };
  //event.preventDefault(); //stop submit
  $.ajax({
    url: '/timeline/addToTimeline/',
    type: 'POST',
    dataType: 'json',
    data: data,
    success: function(data) {
        // borrar caja publicacion
        if (data==true) {
            $(caja_publicacion).css('background-color', 'tomato');
        }else{
            swal({
                title: "Fail",
                text: "Failed to add to timeline.",
                type: "error"
            });
        }
    },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText);
    }
  });


}
