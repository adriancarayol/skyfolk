var countFriendList = 1;
var countPublicationsList = 1;
var countTimeLine = 1;
var lastClickHeart = 0;
var lastClickHate = 0;
var lastClickTag = 0;
var flag_reply = false;

  /* LOADER PARA SKYFOLK */
$(window).load(function() {
    $("#loader").fadeOut("slow");

    var currentPage = window.location.href.split('/')[3];
    var menu = document.getElementById('hor-menu');
    var inputSearch = document.getElementById('id_searchText');
    var verticalMenu = document.getElementById('ver-menu');
    switch (currentPage) {
              case "following":
                $(menu).find('li:nth-child(3)').css('border-bottom','3px solid #1e88e5');
                  break;
              case "profile":
                  $(menu).find('li:nth-child(1)').css('border-bottom','3px solid #1e88e5');
                  break;
              case "search":
                  $(inputSearch).css('border','1px solid #1e88e5');
                  break;
              case "config":
                $(verticalMenu).find('li:nth-child(2)').css('color','#1e88e5');
                break;
              case "messages":
                $(verticalMenu).find(' li:nth-child(3)').css('color','#1e88e5');
                break;
        default:
            break;
    }
    /* Dar color a la opcion activa en el menu, template configuracion. */
    var conf = window.location.href.split('/')[4];
    var menuConfig = document.getElementsByClassName('menu-config');
    switch (conf) {
        case "profile":
            $(menuConfig).find('a:first-child').css('color','#1e88e5');
            break;
        case "password":
            $(menuConfig).find('a:nth-child(2)').css('color', '#1e88e5');
            break;
        case "config":
            $(menuConfig).find('a:nth-child(3)').css('color', '#1e88e5');
            break;
        case "email":
            $(menuConfig).find('a:nth-child(4)').css('color', '#1e88e5');
            break;
        case "privacity":
            $(menuConfig).find('a:nth-child(5)').css('color', '#1e88e5');
            break;
        case "pincode":
            $(menuConfig).find('a:nth-child(6)').css('color', '#1e88e5');
            break;
        default:
            break;
    }

        /* Dar color a la opcion activa en el menu, template mensajes privados. */
    var private_mess = window.location.href.split('/')[4];
    switch (private_mess) {
        case "inbox":
            $('.menu-messages').find('a:first-child').css('color','#1e88e5');
            break;
        case "compose":
            $('.menu-messages').find('a:nth-child(2)').css('color', '#1e88e5');
            break;
        case "outbox":
            $('.menu-messages').find('a:nth-child(3)').css('color', '#1e88e5');
            break;
        case "trash":
            $('.menu-messages').find('a:nth-child(4)').css('color', '#1e88e5');
            break;
        default:
            break;
    }
});

$(document).ready(function () {

    /* Mensaje flotante */
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
    /* DISPLAY MENU */
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

      //Examples of how to assign the ColorBox event to elements (Galeria)
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

    /* Show more - Show less */
    $('#tab-comentarios').find('.wrapper').each(function () {
        var showLimitChar = 90;
        var comment = $(this).find('.wrp-comment');
        var commentValue = comment.text();
        var text = comment.text();
        var show = $(this).find('.show-more a');
        text = text.replace(/\s\s+/g, ' ');

        if (text.length < showLimitChar) {
            $(show).css('display','none');
        }
    });

    $(".show-more a").on("click", function() {

    var $this = $(this);
    var $content = $this.parent().prev("div.comment").find(".wrp-comment");
    var linkText = $this.text().toUpperCase();

    if(linkText === "+ MOSTRAR MÁS"){
        linkText = "- Mostrar menos";
        $content.css('height', 'auto');
    } else {
        linkText = "+ Mostrar más";
        $content.css('height', '2.6em');
    }
        $this.text(linkText);
});

  $('#page-wrapper').find('#close').on('click', function(event) {
    $('#page-wrapper').find('#message2').val('');
    $('#page-wrapper').hide();
  });

  $('.fa-paw').on('click',function() {
      $(".info-paw").fadeToggle(50);
  });

  $('.info-trof').on('click',function() {
    $(".trofeos").fadeToggle(50);
  });

  $('.info-groups').on('click',function() {
    $(".grupos").fadeToggle(50);
  });

  $('#close-trofeos').on('click',function() {
    $(".trofeos").fadeOut(50);
  });

  $('#close-grupos').on('click',function() {
     $(".grupos").fadeOut(50);
  });

  $('#message-form2').on('submit', function(event) {
    event.preventDefault();
    var data = $('#page-wrapper').find('#message-form2').serialize();
    AJAX_submit_publication(data);
  });

  $('button.enviar').on('click', function(event) {
    event.preventDefault();
    var parent_pk = $(this).attr('id').split('-')[1];
    var form = $(this).parent();
    $(form).find('input[name=parent]').val(parent_pk);
    var user_pk = $(form).find('input[name=author]').val();
    var owner_pk = $(form).find('input[name=board_owner]').val();
    var data = $(form).serialize();
    var pks = [user_pk, owner_pk, parent_pk];
    AJAX_submit_publication(data, 'reply', pks);
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
        //var i = $(this).closest('.wrapper');
        //replyComment(i);
        var id_ = $(this).attr("id").slice(6);
        if (flag_reply) {
            $("#"+id_).slideUp("fast");
            flag_reply = false
        }else{
            $("#"+id_).slideDown("fast");
            flag_reply = true
        }
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
        var tag = this;
        if (Date.now() - lastClickTag > 1000) {
            AJAX_add_timeline(caja_publicacion, tag);
            lastClickTag = Date.now();
        } else {
            swal({
              title: ":/",
              text: "Debes esperar 1 segundos para volver a pulsar el botón.",
              timer: 2000,
              showConfirmButton: true,
              type: "warning"
            });
        }
    });

    /* Añadir me gusta a comentario */
    $('.optiones_comentarios').find('#like-heart').on('click', function() {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        if (Date.now() - lastClickHeart > 1000) {
            AJAX_add_like(caja_publicacion, heart);
            lastClickHeart = Date.now();
        } else {
            swal({
              title: ":/",
              text: "Debes esperar 1 segundos para volver a pulsar el botón.",
              timer: 2000,
              showConfirmButton: true,
              type: "warning"
            });
        }
    });

    /* Añadir no me gusta a comentario */

    $('.optiones_comentarios').find('#fa-hate').on('click', function() {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        if (Date.now() - lastClickHate > 1000) {
            AJAX_add_hate(caja_publicacion, heart);
            lastClickHate = Date.now();
        } else {
            swal({
              title: ":/",
              text: "Debes esperar 1 segundos para volver a pulsar el botón.",
              timer: 2000,
              showConfirmButton: true,
              type: "warning"
            });
        }
    });

/* Mostramos y ocultamos notificaciones y chat por la derecha */

  $(".fa-bell").click(function(){
    $("#notification-menu").animate({width: 'toggle'}, 100);
  });


  /* Atajo para enviar comentarios mas rapido */

  $('#page-wrapper').find('#message2').keypress(function(event) {
    //tecla ENTER presinada + Shift
    if (event.keyCode == 13 && event.shiftKey) {
      $('#sendformpubli').click();
    }
  });


  /* Abrir - Cerrar lista de atajos */

  $('.menup .shortcut-keyboard').on('click',function() {
    $('#atajos-keyboard-profile').fadeToggle("fast");
  });

/* ATAJOS DE DECLADO */

/* Abre nuevo mensaje "m" */

  $(document).keypress(function(e){
    var page_wrapper = document.getElementById('page-wrapper');
    var key = e.which;
    if (key == 109 && ($(page_wrapper).is(':hidden')) &&
    !($('input').is(":focus")) &&
    !($('textarea').is(":focus"))) { // Si la tecla pulsada es la m y el div esta oculto, lo mostramos.
        // Si presionas el char 'm' mostará el div para escribir un mensaje.
        $(page_wrapper).toggle();
        $(page_wrapper).find('#message2').focus();
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

$(document).on('keydown', function(e) {
    if (e.keyCode === 27) { // escape
        var messageWrapper = document.getElementById('page-wrapper');
        var ampliado = document.getElementsByClassName('ampliado');
        var atj = document.getElementById('atajos-keyboard-profile');
        var personalInfo = document.getElementsByClassName('info-paw');
        var searchInput = document.getElementById('id_searchText');
        $(messageWrapper).find('#message2').blur(); // Focus del textarea off.
        $(messageWrapper).hide();  // Oculta from para crear comentario.
        $(atj).hide(); // Oculta atajos de teclado.
        $(ampliado).hide(); // Oculta mensaje ampliado.
        $(personalInfo).hide(); // Oculta informacion personal
        $(searchInput).val("");
        $(searchInput).blur();
    }
});

    $(document).on('keydown', function(e) {
    if (e.keyCode === 111 && ($('#atajos-keyboard-profile').is(':hidden')) &&
    !($('input').is(":focus")) &&
    !($('textarea').is(":focus"))) { // escape
      $('#id_searchText').focus(); // Focus del textarea off.
      return false;
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
          $('#tab-comentarios').find('.wrapper').each(function () {
              var text = $(this).find('.wrp-comment').text();
              var show = $(this).find('.show-more a');
              text = text.replace(/\s\s+/g, ' ');
              if (text.length < 45)
              {
                  $(show).css('display','none');
              }

          });
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


/* Para el manejo del tablon de comentarios/seguidores */
  $('#tab-container').easytabs({
        defaultTab: "#li-tab-comentarios",
        animate: true,
        animationSpeed: "fast",
        updateHash: false
  });

    /* Marcar todas las publicaciones como leidas */
    $('#clear-notify').on('click', function() {
        AJAX_mark_all_read();
    });
    /* FIN DOCUMENT READY */
});
/* Para marcar las publicaciones de un usuario como leidas */
function AJAX_mark_all_read() {
  $.ajax({
    url: '/inbox/notifications/mark-all-as-read/',
    data: {
        'csrfmiddlewaretoken': csrftoken
    },
    type: 'POST',
    success: function() {
        $('#notification-menu').find('li').fadeOut("fast");
        $("#live_notify_badge").html(0);
    },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText + e);
    }
  });
}
/* Para marcar una notificacion como leida */
function AJAX_mark_read(obj) {
    var slug = obj.getAttribute('data-notification');
    var url_ = '/inbox/notifications/mark-as-read/' + slug + '/';
  $.ajax({
    url: url_,
    data: {
        'csrfmiddlewaretoken': csrftoken
    },
    type: 'POST',
    success: function() {
        $(obj).parent().fadeOut("fast");
        var currentValue = document.getElementById('live_notify_badge');
        if (parseInt($(currentValue).html()) > 0)
            $(currentValue).html(parseInt($(currentValue).html())-1);
    },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText + e);
    }
  });
}
/* Para eliminar una notificacion */
function AJAX_delete_notification(obj) {
    var slug = obj.getAttribute('data-notification');
    var url_ = '/inbox/notifications/delete/' + slug + '/';
  $.ajax({
    url: url_,
    data: {
        'csrfmiddlewaretoken': csrftoken
    },
    type: 'POST',
    success: function() {
        $(obj).parent().fadeOut("fast");
        var currentValue = document.getElementById('live_notify_badge');
        if (parseInt($(currentValue).html()) > 0)
            $(currentValue).html(parseInt($(currentValue).html())-1);
    },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText + e);
    }
  });
}
function addFriendToHtmlList(item) {

  if (item.user__profile__image) {
    $("#tab-amigos").find("ul.list").append('<li id="friend-' + item.user__id + '"><img src="' + MEDIA_URL + item.user__profile__image + '"  class="friend-avatar img-responsive"><a href="/profile/' + item.user__username + '">' + item.user__first_name + ' ' + item.user__last_name + ' (' + item.user__username + ')</a></li>');

    //SI NO EXISTE LA URL DE LA IMAGEN, SE CAMBIA POR EL AVATAR POR DEFECTO. QUITAR ESTO CUANDO
    //SE PUEDAN SUBIR IMAGENES SIN QUE DESAPAREZCAN MAS TARDE
    imageselector = $("#tab-amigos").find("ul.list #friend-" + item.user__id + " img.friend-avatar")
    URL_CHECK = MEDIA_URL + item.user__profile__image;
    URL_CHANGE = STATIC_URL + 'img/default.png';
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

            //forma chula
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

function addPublicationToHtmlList(data) {

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
    URL_CHANGE = STATIC_URL + 'img/default.png';
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
      } else if (response == 'in_progress'){
          swal({
              title: "Request in progress",
              text: "Your request is to confirm!.",
              timer: 4000,
              showConfirmButton: true
            });
      } else if (response == 'new_petition'){
          swal({
              title: "New petition sent!",
              text: "Wait to confirm!.",
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


function AJAX_respondFriendRequest(id_emitter, status, obj_data) {
  $.ajax({
    type: "POST",
    url: "/respond_friend_request/",
    data: {
      'slug': parseInt(id_emitter),
      'status': status,
      'csrfmiddlewaretoken': csrftoken
    },
    dataType: "json",
    success: function(response) {
      if (response == "added_friend") {
        addItemToFriendList('Nuevo','nuevo');
        sweetAlert("You have added a friend!");
        $('li[data-id='+obj_data+']').fadeOut("fast");
      } else {
          $('li[data-id='+obj_data+']').fadeOut("fast");
      }
    },
    error: function(rs, e) {
      alert(rs.responseText + " " + e);
    }
  });


}


function addNewPublication(type, user_pk, board_owner_pk, parent) {
  if (type=="reply") {
    $.get( "/publication/list/?type=reply&user_pk=" + user_pk + "&board_owner_pk" + board_owner_pk + ",parent="+parent, function(data) {
      $( "#tab-comentarios" ).prepend(data).fadeIn('slow/400/fast')
    })
  } else {
    $.get( "/publication/list/", function(data) {
      if ($("#tab-comentarios").find(".no-comments").length) {
        $("#tab-comentarios").find(".no-comments").remove()
      }
      $("#tab-comentarios").prepend(data).fadeIn('slow/400/fast')
    })
  }
}


function AJAX_submit_publication(data, type, pks) {
  type = typeof type !== 'undefined' ? type : "reply"; //default para type
  $.ajax({
    url: '/publication/',
    type: 'POST',
    dataType: 'json',
    data: data,
    success: function(data) {
      var response = data.response;
      console.log('RESPONSE AQUI');
      console.log(response);
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
        if (type == "reply") {
          $('#page-wrapper').fadeOut("fast"); // Ocultamos el DIV al publicar un mensaje.
          $("#caja-comentario-"+pks[2]).slideUp(); // Ocultamos textarea de respuesta
        }
        },
    error: function(rs, e) {
      alert('ERROR: ' + rs.responseText + " " + e)
    }
  }).done(function() {
    addNewPublication(type, pks[0], pks[1], pks[2])
  })


}


/*
function showRequest(id_profile, username) {
  var unique_id = $.gritter.add({
    // (string | mandatory) the heading of the notification
    title: '<a href="/profile/'+username+'">'+username+'</a>' + ' wants to follow you!',
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
    id_emitter: id_profile

  });

}
*/

/*PETICION AJAX PARA AGREGAR AMIGO*/
function AJAX_requestfriend(status) {
    var slug = $("#profileId").html();
    if (status == "noabort") {
      $.ajax({
        type: "POST",
        url: "/request_friend/",
        data: {
          'slug': slug,
          'csrfmiddlewaretoken': csrftoken
        },
        //data: {'slug': $("#profileId").html()},
        dataType: "json",
        success: function(response) {
          if (response == "isfriend") {
              swal({
                title: "¡Ya es tu amigo!",
                type: "warning",
                animation: "slide-from-top",
                showConfirmButton: true,
                showCancelButton: true,
                confirmButtonColor: "#DD6B55",
                confirmButtonText: "Unfollow",
                cancelButtonText: "Ok, fine!",
                closeOnConfirm: true
            },
              function() {
                  AJAX_remove_relationship(slug);
              });
          } else if (response == "inprogress") {
                $('#addfriend').replaceWith('<span class="fa fa-clock-o" id="follow_request" title="En proceso" onclick="AJAX_remove_request_friend();">'+' '+'</div>');
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
/* Eliminar relacion entre dos usuarios */
function AJAX_remove_relationship(slug) {
    $.ajax({
        type: 'POST',
        url: '/remove_relationship/',
        data: {
          'slug': slug,
          'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function(response) {
            if (response == true) {
                var currentValue = document.getElementById('followers-stats');
                $(currentValue).html(parseInt($(currentValue).html())-1);
            } else if (response == false) {
                swal("Ha surgido un error, inténtalo de nuevo más tarde :-(");
            }
        }, error: function(rs, e) {
            swal(rs.responseText + " " + e);
        }
    });
}

/* Eliminar peticion de amistad */
function AJAX_remove_request_friend() {
    var slug = $("#profileId").html();
    $.ajax({
        type: 'POST',
        url: '/remove_request_follow/',
        data: {
          'slug': slug,
          'status': 'cancel',
          'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function(response) {
            if (response == true) {
                $('#follow_request').replaceWith('<span id="addfriend" class="fa fa-plus" title="Seguir" onclick=AJAX_requestfriend("noabort");></span>');
            } else if (response == false) {
                swal("Ha surgido un error, inténtalo de nuevo más tarde :-(");
            }
        }, error: function(rs, e) {
            swal(rs.responseText + " " + e);
        }
    });
}

/* Ocultar menu vertical al hacer click fuera de el */
$(document).click(function(event) {
    if(!$(event.target).closest('#toggle').length) {
        if($('#toggle').is(":visible")) {
            $('#toggle').hide();
            $('.fa-bars').removeClass('fa-bars-rotate');
        }
    }
});

/* Ocultar menu de notificaciones al hacer click fuera de él */
$(document).click(function(event) {
    if (!$(event.target).closest('#notification-menu').length) {
        if (!$(event.target).closest('.fa-bell').length) {
            if ($('#notification-menu').is(":visible")) {
                $('#notification-menu').animate({width: 'toggle'}, 100);
                $('.fa-bars').removeClass('fa-bars-rotate');
            }
        }
    }
});

function addItemToFriendList(name, lastname) {

  $("#tab-amigos").find("ul").append('<li><img src="{{STATIC_URL}}img/generic-avatar.png" class="img-responsive"><a>' + name + ' ' + lastname + '</a></li>');

}


/*****************************************************/
/********** AJAX para botones de comentarios *********/
/*****************************************************/

function AJAX_delete_publication(caja_publicacion) {
  var id_pub = $(caja_publicacion).attr('id').split('-')[1];  // obtengo id
  var id_user = $(caja_publicacion).data('id'); // obtengo id
  var data = {
           userprofile_id: id_user,
           publication_id: id_pub,
           'csrfmiddlewaretoken': csrftoken
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
           publication_id: id_pub,
           'csrfmiddlewaretoken': csrftoken
        };
  //event.preventDefault(); //stop submit
  $.ajax({
    url: '/publication/add_like/',
    type: 'POST',
    dataType: 'json',
    data: data,
    success: function(data) {
      var response = data.response;
      var status = data.statuslike;
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
                text: "¡No puedes dar me gusta a este comentario!",
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
/******* AJAX para añadir no me gusta a comentario ***/
/*****************************************************/

function AJAX_add_hate(caja_publicacion, heart) {
  var id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
  var id_user = $(caja_publicacion).data('id'); // obtengo id
  var data = {
           userprofile_id: id_user,
           publication_id: id_pub,
           'csrfmiddlewaretoken': csrftoken
        };
  //event.preventDefault(); //stop submit
  $.ajax({
    url: '/publication/add_hate/',
    type: 'POST',
    dataType: 'json',
    data: data,
    success: function(data) {
      var statusOk = 1;
      var statusNo = 2;
      var response = data.response;
      var status = data.statuslike;
      var numLikes = heart;
      var countLikes = numLikes.innerHTML;
        if (response==true) {
            $(heart).css('color','#ba68c8');
            if (status == statusOk) {
              countLikes++;
            } else if (status == statusNo) {
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
                text: "¡No puedes dar no me gusta a este comentario!",
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

function AJAX_add_timeline(caja_publicacion, tag) {
  var id_pub = $(caja_publicacion).attr('id').split('-')[1];  // obtengo id
  var id_user = $(caja_publicacion).data('id'); // obtengo id
  var data = {
           userprofile_id: id_user,
           publication_id: id_pub,
           'csrfmiddlewaretoken': csrftoken
       };
  //event.preventDefault(); //stop submit
  $.ajax({
    url: '/timeline/add_to_timeline/',
    type: 'POST',
    dataType: 'json',
    data: data,
    success: function(data) {
        // borrar caja publicacion
        if (data==true) {
            $(tag).css('color', '#bbdefb');
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
/********** AJAX para borrado de timeline ***********/
/****************************************************/

function AJAX_delete_timeline(div_timeline) {
  var id_pub = $(div_timeline).attr('id').split('-')[1];  // obtengo id
  var id_user = $(div_timeline).data('id'); // obtengo id
  var data = {
           userprofile_id: id_user,
           timeline_id: id_pub,
           'csrfmiddlewaretoken': csrftoken
       };
  //alert("id pub: " + id_pub + " id_user: " + id_user);
  //event.preventDefault(); //stop submit
  $.ajax({
    url: '/timeline/remove_timeline/',
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
/**********              UTIL                *********/
/*****************************************************/

function is_numeric(value) {
    var is_number =  /^\d+$/.test(value);
    return is_number;
}

function serializedToJSON(data) {
    //from -> http://stackoverflow.com/questions/23287067/converting-serialized-forms-data-to-json-object
    data = data.split("&");
    var obj={};
    for(var key in data)
    {
        obj[data[key].split("=")[0]] = data[key].split("=")[1]
    }

    return obj
}
