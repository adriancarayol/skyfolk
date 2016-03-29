var countFriendList = 1;
var countPublicationsList = 1;
var countTimeLine = 1;

  /* LOADER PARA SKYFOLK */
$(window).load(function() {
    $("#loader").fadeOut("slow");

    var currentPage = window.location.href.split('/')[3];
    switch (currentPage) {
              case "friends":
                $('.oldMenu').find('li:nth-child(3)').css('border-bottom','3px solid #1e88e5');
                  break;
              case "profile":
                  $('.oldMenu').find('li:nth-child(1)').css('border-bottom','3px solid #1e88e5');
                  break;
              case "search":
                  $('#id_searchText').css('border','1px solid #1e88e5');
                  break;
              case "config":
                $('.menup').find('li:nth-child(2)').css('color','#1e88e5');
                break;
              case "messages":
                $('.menup').find(' li:nth-child(3)').css('color','#1e88e5');
                break;
        default:
            break;
    }
    /* Dar color a la opcion activa en el menu, template configuracion. */
    var conf = window.location.href.split('/')[4];
    switch (conf) {
        case "profile":
            $('.menu-config').find('a:first-child').css('color','#1e88e5');
            break;
        case "password":
            $('.menu-config').find('a:nth-child(2)').css('color', '#1e88e5');
            break;
        default:
            break;
    }
});

$(document).ready(function () {



    /* Show more - Show less */

    $('#tab-comentarios').find('.wrapper').each(function () {
    var text = $(this).find('.wrp-comment').text();
    var show = $(this).find('.show-more a');

    if (text.length < 60)
    {
        $(show).css('display','none');
    }

  });

    $(".show-more a").on("click", function() {

    var $this = $(this);
    var $content = $this.parent().prev("div.comment");
    var linkText = $this.text().toUpperCase();

    if(linkText === "+ MOSTRAR MÁS"){
        linkText = "- Mostrar menos";
        $content.css('height', 'auto');
    } else {
        linkText = "+ Mostrar más";
        $content.css('height', '3em');
    }

    $this.text(linkText);
});

  $('#page-wrapper').find('#close').on('click', function(event) {

    $('#page-wrapper').hide();
  });

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

  $('#atajos-keyboard-profile').find('.atajos-title .fa-close').on('click',function() {
    $('#atajos-keyboard-profile').hide();
  });

  $('#configurationOnProfile').on('click', function() {
    if ($('.ventana-pin').is(':visible')) {
      $('html, body').removeClass('body-inConf');
      $('.ventana-pin').fadeOut("fast");
    } else {
      $('html, body').addClass('body-inConf');
      $('.ventana-pin').fadeIn("fast");
    }
  });

  /* Abrir respuesta a comentario */
    $('.fa-reply').on('click', function() {
        var i = $(this).closest('.wrapper');
        replyComment(i);
    });

    function replyComment(caja_pub) {
        var id_comment = $(caja_pub).attr('id').split('-')[1];
        var commentReply = document.getElementById('actual-' + id_comment);
        $(commentReply).toggleClass("reply-actual-message-show");
    }
  /* Expandir comentario */

 $('.fa-expand').on('click', function() {
    var caja_pub = $(this).closest('.wrapper');
    expandComment(caja_pub);
 });

 function expandComment(caja_pub) {
    var id_pub = $(caja_pub).attr('id').split('-')[1];  // obtengo id
    var commentToExpand = document.getElementById('expand-' + id_pub);
    $(commentToExpand).fadeToggle("fast");
 }

 /* Cerrar comentario expandido */

 $('.cerrar_ampliado').on('click', function() {
 	var expand = $(this).closest('.ampliado');
 	closeExpand(expand);
 });

 function closeExpand(expand) {
 	var c = $(expand).attr('id').split('-')[1];
 	var toClose = document.getElementById('expand-' + c);
 	$(toClose).hide();
 }

/*
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

  /* Borrar timeline */

  $('#tab-timeline').find('.controles .fa-trash').on('click', function() {
    var div_timeline = $(this).closest('.line');
    swal({
      title: "Are you sure?",
      text: "You will not be able to recover this history!",
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
        AJAX_delete_timeline(div_timeline);
      }
    });
});

  /* Agregar Amigo por medio de PIN */
  $('#agregar-amigo').on('click', function() {
      swal({
            title: "Add new friend!",
            text: "Insert the friend's username or PIN",
            type: "input",
            animation: "slide-from-top",
            showConfirmButton: true,
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Add it!",
            cancelButtonText: "Cancel!",
            closeOnConfirm: false,
            showLoaderOnConfirm: true
        }, function(inputValue) {
          if (inputValue === false) return false;
          if (inputValue === "") {
            swal.showInputError("You need to write something!");
            return false
          }
          if ((inputValue.length != 9) && (is_numeric(inputValue))) {
            swal.showInputError("Wrong PIN format!");
            return false
          }
          var tipo;
          if (!is_numeric(inputValue)) {
              tipo = 'username';
          } else {
              tipo = 'pin'
          }
          AJAX_addNewFriendByUsernameOrPin(inputValue, tipo);
        });
  });

    /* Agregar timeline */
    $('.optiones_comentarios').find('.fa-tag').on('click', function() {
        var caja_publicacion = $(this).closest('.wrapper');
        alert('VAS A AÑADIR EL COMENTARIO A TU TIMELINE');
        AJAX_add_timeline(caja_publicacion);
    });

    /* Añadir me gusta a comentario */
    $('.optiones_comentarios').find('#like-heart').on('click', function() {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        AJAX_add_like(caja_publicacion, heart);
    });

/* Mostramos y ocultamos notificaciones y chat por la derecha */

  $(".fa-bell").click(function(){
    $(".nav-vertical-and-chat").animate({width: 'toggle'},100);
  });


  /* Atajo para enviar comentarios mas rapido */

  $('#page-wrapper').find('#message2').keypress(function(event) {
    //tecla ENTER presinada + Shift
    if (event.keyCode == 13 && event.shiftKey) {
      $('#sendformpubli').click();
    }
  });



  /* Abrir crear/cerrar grupo en search.html */

  $('.btn-floating').on('click', function () {
        $('.crear-grupo').toggle("fast",function() {
    });
  });

  $('#cerrar_grupo').on('click',function() {
    $('.crear-grupo').hide();
  });

  /* Abrir - Cerrar lista de atajos */

  $('.menup .shortcut-keyboard').on('click',function() {
    $('#atajos-keyboard-profile').fadeToggle("fast");
  });

/* ATAJOS DE DECLADO */

/* Abre nuevo mensaje "m" */

  $(document).keypress(function(e){
    var key = e.which;
    if (key == 109 && ($('#page-wrapper').is(':hidden')) &&
    !($('input').is(":focus")) &&
    !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
        // Si presionas el char 'm' mostará el div para escribir un mensaje.
        $('#page-wrapper').toggle();
        $('#page-wrapper').find('#message2').focus();
    }
  });
/* Abre atajos "a" */

$(document).keypress(function(e){
    var key = e.which;
    if (key == 97 && ($('#atajos-keyboard-profile').is(':hidden')) &&
    !($('input').is(":focus")) &&
    !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
        // Si presionas el char 'm' mostará el div para escribir un mensaje.
        $('#atajos-keyboard-profile').show();
    }
});

/* Cierra todas las ventajas emergentes. */

$( document ).on('keydown', function(e) {
    if ( e.keyCode === 27 ) { // escape

        $('#page-wrapper').find('#message2').blur(); // Focus del textarea off.
        $('#page-wrapper').hide();  // Oculta from para crear comentario.
        $('#atajos-keyboard-profile').hide(); // Oculta atajos de teclado.
        $('.ampliado').hide(); // Oculta mensaje ampliado.

    }
});

    $( document ).on('keydown', function(e) {
    if ( e.keyCode === 111 && ($('#atajos-keyboard-profile').is(':hidden')) &&
    !($('input').is(":focus")) &&
    !($('textarea').is(":focus"))) { // escape
        $('#id_searchText').focus(); // Focus del textarea off.
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
          for (var i = 0; i < response.length; i++) {
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
          for (var i = 0; i < response.length; i++) {
            addPublicationToHtmlList(response[i]);
          }
          // $('#tab-comentarios').load(location.href + " #tab-comentarios");
          //refresca plugin shorten
          /*$(".comment").shorten({
            "showChars": 145
          }); */
	    if ($('#tab-comentarios').find('.wrapper').height() > 145) {
	     $('#tab-comentarios').find('.wrapper').css('height','auto');
	   }
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
        updateHash: false


  });

/* FIN DOCUMENT READY */
});

function addFriendToHtmlList(item) {

  if (item.user__profile__image) {
    $("#tab-amigos").find("ul.list").append('<li id="friend-' + item.user__id + '"><img src="' + MEDIA_URL + item.user__profile__image + '"  class="friend-avatar img-responsive"><a href="/profile/' + item.user__username + '">' + item.user__first_name + ' ' + item.user__last_name + ' (' + item.user__username + ')</a></li>');

    //SI NO EXISTE LA URL DE LA IMAGEN, SE CAMBIA POR EL AVATAR POR DEFECTO. QUITAR ESTO CUANDO
    //SE PUEDAN SUBIR IMAGENES SIN QUE DESAPAREZCAN MAS TARDE
    imageselector = $("#tab-amigos").find("ul.list #friend-" + item.user__id + " img.friend-avatar")
    URL_CHECK = MEDIA_URL + item.user__profile__image;
    URL_CHANGE = STATIC_URL + 'img/nuevo.png';
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
    $("#tab-amigos").find("ul.list").append('<li id="friend-' + item.user__id + '"><img src="' + STATIC_URL + 'img/generic-avatar.png" class="friend-avatar img-responsive"><a href="/profile/' + item.user__username + '">' + item.user__first_name + ' ' + item.user__last_name + ' (' + item.user__username + ')</a></li>');
  }



}

function addPublicationToHtmlList(item) {

  if (item.user__profile__image) {
    $("#tab-comentarios").append('<div class="wrapper" id="pub-' + item.from_publication__id + '">\
              <div id="box">\
                  <span id="check-' + item.from_publication__id + '" class="zoom-pub"><i class="fa fa-expand fa-lg"></i></span>\
                  <div class="ampliado" id="expand-' + item.from_publication__id +'">\
                    <div class="nombre_image">\
                    <ul>\
                    <li><i class="first">' + item.user__first_name + item.user__last_name + '</i></li>\
                    <li><a class="name" href="/profile/' + item.user__username + '" >' + item.user__username + '</a></li>\
                    </ul>\
                    <img src="' + MEDIA_URL + item.user__profile__image + '" alt="img" class="usr-img img-responsive">\
                    </div>\
                    <div class="parrafo comment-tab">\
                    <a target="_blank">' + item.from_publication__created + '</a><br><br>' + item.from_publication__content + '\
                    </div>\
                    <div class="text_area">\
                      <textarea placeholder="Escribe tu mensaje..."></textarea>\
                      <div class="botones_ampliado">\
                        <button class="enviar_ampliado"></i class="fa fa-paper-plane"></i>Enviar</button>\
                        <button class="cerrar_ampliado"></i class="fa fa-close"></i><label for="check-' + item.from_publication__id + '">Cerrar</label></button>\
                        <button class="difundir_ampliado"></i class="fa fa-bullhorn"></i> Difundir mensaje</button>\
                        <button class="foto_ampliado"></i class="fa fa-paperclip"></i> Añadir archivo</button>\
                        <button class="localizacion_ampliado"></i class="fa fa-map-marker"></i> Añadir localización</button>\
                      </div>\
                  </div>\
                  <div class="image">\
                  <img src="' + MEDIA_URL + item.user__profile__image + '" alt="img" class="usr-img img-responsive">\
                  </div>\
                  </div>\
            </div>\
            <article class="articulo">\
              <h2 class="h22"><a href="/profile/' + item.user__username + '" >' + item.user__username + '</a> ha publicado: </h2>\
              <div class="parrafo comment">\
                <a target="_blank">' + item.from_publication__created + '</a><br>\
                <div class="wrp-comment">' + item.from_publication__content + '</div>\
              </div>\
              <div class="show-more">\
                <a href="#">+ Mostrar más</a>\
              </div>\
              <div class="optiones_comentarios">\
              </div>\
            </article>\
        </div>');



    //SI NO EXISTE LA URL DE LA IMAGEN, SE CAMBIA POR EL AVATAR POR DEFECTO. QUITAR ESTO CUANDO
    //SE PUEDAN SUBIR IMAGENES SIN QUE DESAPAREZCAN MAS TARDE
    imageselector = $("#tab-comentarios").find("#pub-" + item.from_publication__id + " img.pub-avatar");
    URL_CHECK = MEDIA_URL + item.user__profile__image;
    URL_CHANGE = STATIC_URL + 'img/nuevo.png';
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
		       <li><i class="fa fa-trash"></i></li>\
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
  if (status == "noabort") $.ajax({
      type: "POST",
      url: "/like_profile/",
      data: {
          'slug': $("#profileId").html(),
          'csrfmiddlewaretoken': csrftoken
      },
      //data: {'slug': $("#profileId").html()},
      dataType: "json",
      success: function (response) {

          if (response == "like") {

              $("#ilike_profile").css('color', '#ec407a');

              //Aumentamos el valor del campo
              $("#likes").find("strong").html(parseInt($("#likes").find("strong").html()) + 1);

          } else if (response == "nolike") {

              $("#ilike_profile").css('color', '#46494c');

              if ($("#likes").find("strong").html() > 0) {
                  //Decrementar
                  $("#likes").find("strong").html(parseInt($("#likes").find("strong").html()) - 1);
              }

          } else {

          }
      },
      error: function (rs, e) {
          alert(rs.responseText);
      }
  }); else if (status == "anonymous") {
    alert("Debe estar registrado");
  }

}


function AJAX_addNewFriendByUsernameOrPin(valor, tipo) {
  $.ajax({
    type: "POST",
    url: "/add_friend_by_pin/",
    data: {
      'valor': valor,
      'tipo': tipo,
      'csrfmiddlewaretoken': csrftoken
    },
    dataType: "json",
    success: function(response) {
      if (response == "added_friend") {
          swal({
              title: "Success!",
              text: "You have added a friend!",
              timer: 4000,
              showConfirmButton: true
            });
      } else if (response == 'your_own_pin') {
          swal({
              title: "Wait a moment!",
              text: "It's your own pin!",
              timer: 4000,
              showConfirmButton: true
            });
      } else if (response == 'your_own_username') {
          swal({
              title: "Wait a moment!",
              text: "It's your own username!",
              timer: 4000,
              showConfirmButton: true
            });
      } else if (response == 'its_your_friend') {
          swal({
              title: "Wait a moment!",
              text: "It's already your friend!",
              timer: 4000,
              showConfirmButton: true
            });
      } else if (response == 'no_added_friend'){
          swal({
              title: "We have a problem",
              text: "Friend no added",
              timer: 4000,
              showConfirmButton: true
            });
      } else if (response == 'no_match'){
          swal({
              title: "We have a problem",
              text: "This username or pin no exists.",
              timer: 4000,
              showConfirmButton: true
            });
      }
    },
    error: function(rs, e) {
      alert(rs.responseText + " " + e);
    }
  });


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
        addItemToFriendList('Nuevo','nuevo');
        sweetAlert("You have added a friend!");


      } else {

      }
    },
    error: function(rs, e) {
      alert(rs.responseText + " " + e);
    }
  });


}


function AJAX_submit_publication() {
  $.ajax({
    url: '/publication/',
    type: 'POST',
    dataType: 'json',
    data: $('#page-wrapper').find('#message-form2').serialize(),
    success: function(data) {
      var content = data.content
      var response = data.response;
      var username = data.username; // Perfil al que va la publicacion
      var emittername = data.emittername; // Emisor del mensaje
      if (response == true) {
        swal({
          title: "Success!",
          text: "You have successfully posted!",
          type: "success",
          timer: 900,
          animation: "slide-from-top",
          showConfirmButton: false
        });
      } else {
        swal({
          title: "",
          text: "Failed to publish",
    type: "error"
        });
      }
        $('#page-wrapper').fadeOut("fast"); // Ocultamos el DIV al publicar un mensaje.
        },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText + " " + e);
    }
  });


}



function showRequest(id_profile, username) {

  var unique_id = $.gritter.add({
    // (string | mandatory) the heading of the notification
    title: '<a href="/profile/'+username+'">'+username+'</a>' + ' wants to be your friend!',
    // (string | mandatory) the text inside the notification
    text: '',
    // (string | optional) the image to display on the left
    image: '../../static/img/nuevo.png',
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

$(document).ready(function() {
  //Examples of how to assign the ColorBox event to elements
  $(".inline").colorbox({
    inline: true,
    width: "80%"
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
          alert(rs.responseText + " " + e);
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

/* Ocultar menu vertical al hacer click fuera de el */

$(document).click(function(event) {
    if(!$(event.target).closest('#toggle').length) {
        if($('#toggle').is(":visible")) {
            $('#toggle').hide();
            $('.fa-bars').removeClass('fa-bars-rotate');
        }
    }
})


/* Mensaje flotante */
$(document).ready(function() {
  $("#publish2, #compose-new-no-comments, #publish").click(function()  {
    $("#page-wrapper").each(function() {
      displaying = $(this).css("display");
      $("#page-wrapper").find("#message2").val('');
      if (displaying == "none") {
        $(this).fadeOut('slow', function() {
          $(this).css("display", "block");
        });
          $(this).find('#message2').focus();
      } else {
          $(this).find('#message2').blur();
        $(this).fadeIn('slow', function() {
          $(this).css("display", "none");
        });
      }
    });
  });
});

function addItemToFriendList(name, lastname) {

  $("#tab-amigos").find("ul").append('<li><img src="{{STATIC_URL}}img/generic-avatar.png" class="img-responsive"><a>' + name + ' ' + lastname + '</a></li>');

}


/*****************************************************/
/********** AJAX para borrado de timeline ***********/
/****************************************************/

function AJAX_delete_timeline(div_timeline) {
  var id_pub = $(div_timeline).attr('id').split('-')[1];  // obtengo id
  var id_user = $(div_timeline).data('id'); // obtengo id
  var data = {
           userprofile_id: id_user,
           timeline_id: id_pub
       };
  //alert("id pub: " + id_pub + " id_user: " + id_user);
  //event.preventDefault(); //stop submit
  $.ajax({
    url: '/timeline/removeTimeline/',
    type: 'POST',
    dataType: 'json',
    data: data,
    success: function(data) {
        // borrar caja timeline
        if (data==true) {
            $(div_timeline).fadeToggle("fast");
        }else{
            swal({
                title: "Fail",
                text: "Failed to delete publish.",
                type: "error"
            });
        }
    },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText + " " + e);
    }
  });
}
/*****************************************************/
/********** AJAX para botones de comentarios *********/
/*****************************************************/

function AJAX_delete_publication(caja_publicacion) {
  var id_pub = $(caja_publicacion).attr('id').split('-')[1];  // obtengo id
  var id_user = $(caja_publicacion).data('id'); // obtengo id
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
      alert('ERROR: ' + rs.responseText + ' ' + e);
    }
  });
}

/*****************************************************/
/********** AJAX para añadir me gusta a comentario ***/
/*****************************************************/

function AJAX_add_like(caja_publicacion, heart) {
  var id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
  var id_user = $(caja_publicacion).data('id'); // obtengo id
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
      var response = data.response;
      var status = data.statusLike;
      var numLikes = heart;
      var countLikes = numLikes.innerHTML;
        if (response==true) {
            $(heart).css('color','#f06292');
            if (status == 1) {
              countLikes++;
            } else if (status == 2) {
              $(heart).css('color','#555');
              countLikes--;
            }
            if (countLikes == 0) {
              numLikes.innerHTML = " ";
            } else {
              numLikes.innerHTML = " " + countLikes;
            }
        } else{
            swal({
                title: ":-(",
                text: "¡No puedes dar like a este comentario!",
                timer: 1000,
                animation: "slide-from-bottom",
                showConfirmButton: false,
                type: "error"
            });
        }
    },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText + e);
    }
  });
}

/*****************************************************/
/********** AJAX para agregar al TIMELINE *********/
/*****************************************************/

function AJAX_add_timeline(caja_publicacion) {
  var id_pub = $(caja_publicacion).attr('id').split('-')[1];  // obtengo id
  var id_user = $(caja_publicacion).data('id'); // obtengo id
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
      alert('ERROR: ' + rs.responseText + e);
    }
  });
}

/*****************************************************/
/**********              UTIL                *********/
/*****************************************************/

function is_numeric(value) {
    var is_number =  /^\d+$/.test(value);
    return is_number;
}
