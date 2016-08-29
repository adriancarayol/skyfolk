var countFriendList = 1;
var countPublicationsList = 1;
var countTimeLine = 1;
var lastClickHeart = 0;
var lastClickHate = 0;
var lastClickTag = 0;
var flag_reply = false;



$(document).ready(function () {
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

  $('.fa-paw').on('click',function() {
      $(".info-paw").show();
  });

  $('.info-trof').on('click',function() {
    $(".trofeos").show();
  });

  $('.info-groups').on('click',function() {
    $(".grupos").show();
  });

  $('#close-trofeos').on('click',function() {
    $(".trofeos").hide();
  });

  $('#close-grupos').on('click',function() {
     $(".grupos").hide();
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
    $('#options-comments').on('click', '.fa-reply', function() {
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
  $('#tab-comentarios').on('click', '#options-comments .fa-trash', function() {
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
    var div_timeline = $(this).closest('.timeline-pub');
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


    /* Agregar timeline */
    $(document).on('click', '#options-comments .fa-tag', function() {
        var caja_publicacion = $(this).closest('.wrapper');
        var tag = this;
        if (Date.now() - lastClickTag > 1000) {
            AJAX_add_timeline(caja_publicacion, tag, "publication");
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
    $(document).on('click', '#options-comments #like-heart', function() {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        if (Date.now() - lastClickHeart > 1000) {
            AJAX_add_like(caja_publicacion, heart, "publication");
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
    $(document).on('click', '#options-comments #fa-hate', function() {
        var caja_publicacion = $(this).closest('.wrapper');
        var heart = this;
        if (Date.now() - lastClickHate > 1000) {
            AJAX_add_hate(caja_publicacion, heart, "publication");
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

    /* Añadir publicacion de timeline a mi timeline */
        $('#wrapperx-timeline').find('#controls-timeline').find('#add-timeline').on('click', function() {
        var caja_publicacion = $(this).closest('.timeline-pub');
        var tag = this;
        if (Date.now() - lastClickTag > 1000) {
            AJAX_add_timeline(caja_publicacion, tag, "timeline");
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
    /* Añadir me gusta a comentario en timeline */
    $('#wrapperx-timeline').find('#controls-timeline').find('#like-heart-timeline').on('click', function() {
        var caja_publicacion = $(this).closest('.timeline-pub');
        var heart = this;
        if (Date.now() - lastClickHate > 1000) {
            AJAX_add_like(caja_publicacion, heart, "timeline");
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
    /* Añadir no me gusta a comentario en timeline */
        $('#wrapperx-timeline').find('#controls-timeline').find('#fa-hate-timeline').on('click', function() {
        var caja_publicacion = $(this).closest('.timeline-pub');
        var heart = this;
        if (Date.now() - lastClickHate > 1000) {
            AJAX_add_hate(caja_publicacion, heart, "timeline");
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

    $('#personal-card-info').find('#bloq-user').on('click', function () {
        var obj = document.getElementById('info-user-name-profile'),
            username = obj.getAttribute('data-id'),
            buttonBan = $(this);
        swal({
          title: "Bloquear a " + username,
          text: username + " no podrá seguirte, enviarte mensajes ni ver tu contenido.",
          type: "warning",
          animation: "slide-from-top",
          showConfirmButton: true,
          showCancelButton: true,
          confirmButtonColor: "#DD6B55",
          confirmButtonText: "Bloquear",
          cancelButtonText: "Cancelar",
          closeOnConfirm: true
        }, function(isConfirm) {
          if (isConfirm) {
            AJAX_bloq_user(buttonBan);
          }
        });
    });

    $(this).click(function(event) {
        if (!$(event.target).closest('#personal-card-info').length) {
            if (!$(event.target).closest('.fa-paw').length) {
                if ($('#personal-card-info').is(":visible")) {
                    $('#personal-card-info').hide();
                }
            }
        }
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
              <div class="options_comentarios">\
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
              <div class="options_comentarios">\
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

/*PETICION AJAX PARA 'I LIKE' DEL PERFIL*/
function AJAX_likeprofile(status) {
  if (status == "noabort") $.ajax({
      type: "POST",
      url: "/like_profile/",
      data: {
          'slug': $("#profileId").html(),
          'csrfmiddlewaretoken': csrftoken
      },
      dataType: "json",
      success: function (response) {
          if (response == "like") {
              $("#ilike_profile").css('color', '#ec407a');
              $("#likes").find("strong").html(parseInt($("#likes").find("strong").html()) + 1);
          } else if (response == "nolike") {
              $("#ilike_profile").css('color', '#46494c');
              if ($("#likes").find("strong").html() > 0) {
                  $("#likes").find("strong").html(parseInt($("#likes").find("strong").html()) - 1);
              }
          } else if (response == "blocked") {
              swal({
                  title: "Vaya... algo no está bien.",
                  text: "Si quieres dar un like, antes debes desbloquear este perfil.",
                  timer: 4000,
                  showConfirmButton: true,
                  type: "error"
            });
          } else {
            console.log("...");
          }
      },
      error: function (rs, e) {
          alert(rs.responseText);
      }
  }); else if (status == "anonymous") {
    alert("Debe estar registrado");
  }

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

function AJAX_add_like(caja_publicacion, heart, type) {
  var id_pub;
  if (type.localeCompare("publication") == 0) {
      id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
  } else if (type.localeCompare("timeline") == 0) {
      id_pub = $(caja_publicacion).data('publication'); // obtengo id
  }
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

function AJAX_add_hate(caja_publicacion, heart, type) {
  var id_pub;
  if (type.localeCompare("publication") == 0) {
      id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
  } else if (type.localeCompare("timeline") == 0) {
      id_pub = $(caja_publicacion).data('publication'); // obtengo id
  }
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
            if (status == statusOk) {
              $(heart).css('color','#ba68c8');

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

function AJAX_add_timeline(caja_publicacion, tag, type) {
  var id_pub;
  if (type.localeCompare("publication") == 0) {
      id_pub = $(caja_publicacion).attr('id').split('-')[1]; // obtengo id
  } else if (type.localeCompare("timeline") == 0) {
      id_pub = $(caja_publicacion).data('publication'); // obtengo id
  }
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

/***** AJAX PARA BLOQUEAR USUARIO *****/
function AJAX_bloq_user(buttonBan) {
    var id_user = $("#profileId").html();
    $.ajax({
        type: 'POST',
        url: '/bloq_user/',
        data: {
            'id_user': id_user,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (data) {
            if (data.response == true) {
                $(buttonBan).css('color', '#FF6347');
                if (data.status == "none" || data.status == "isfollow") {
                    $('#addfriend').replaceWith('<span class="fa fa-ban" id="bloq-user-span" title="Bloqueado" onclick="AJAX_remove_bloq();">'+' '+'</span>');
                } else if (data.status == "inprogress") {
                    $('#follow_request').replaceWith('<span class="fa fa-ban" id="bloq-user-span" title="Bloqueado" onclick="AJAX_remove_bloq();">'+' '+'</span>');
                }
                if (data.haslike == "liked") {
                    $("#ilike_profile").css('color', '#46494c');
                    var obj_likes = document.getElementById('likes');
                    if ($(obj_likes).find("strong").html() > 0) {
                        $(obj_likes).find("strong").html(parseInt($(obj_likes).find("strong").html()) - 1);
                }
                }
            } else {
                swal({
                  title: "Tenemos un problema...",
                  text: "Hubo un problema con su petición.",
                  timer: 4000,
                  showConfirmButton: true
                });
            }
        }, error: function (rs, e) {
            alert(rs.responseText + " " + e);
        }
    });
}

function AJAX_remove_bloq() {
    $.ajax({
        type: 'POST',
        url: '/remove_blocked/',
        data: {
            'slug': $("#profileId").html(),
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: "json",
        success: function (response) {
            if (response == true) {
                $('#bloq-user-span').replaceWith('<span id="addfriend" class="fa fa-plus" title="Seguir" style="color:#555 !important;" onclick=AJAX_requestfriend("noabort");>'+' '+'</span>');
                $('#bloq-user').css('color', '#555');
            } else {
                swal({
                  title: "Tenemos un problema...",
                  text: "Hubo un problema con su petición.",
                  timer: 4000,
                  showConfirmButton: true
                });
            }
        }, error: function (rs, e) {
            alert(rs.responseText + " " + e);
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
