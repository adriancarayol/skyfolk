$(document).ready(function(){
   $("#Menu").click(function () {
      $("#panel").each(function() {
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
	document.getElementById("widget").style.opacity = "0.9";
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
/*Mensaje de audio */
var error = function(e) {
 console.log('¡No se te escucha!', e);
 };
var exito = function(s) {
 var context = new webkitAudioContext(); //Conectamos con nuestra entrada de audio
 var flujo = context.createMediaStreamSource(s); //Obtenemos el flujo de datos desde la fuente
 recorder = new Recorder(flujo); //Todo el flujo de datos lo pasamos a nuestra libreria para procesarlo en esta instancia
 recorder.record(); //Ejecutamos la función para procesarlo
 }
//Convertirmos el objeto en URL
 window.URL = window.URL || window.webkitURL;
 navigator.getUserMedia = navigator.getUserMedia || navigator.webkitGetUserMedia || navigator.mozGetUserMedia || navigator.msGetUserMedia;
var recorder; //Es nuestra variable para usar la libreria Recorder.js
 var audio = document.querySelector('audio'); //Seleccionamos la etiqueta audio para enviarte el audio y escucharla
//Funcion para iniciar el grabado
 function grabar() {
 if (navigator.getUserMedia) { //Preguntamos si nuestro navegador es compatible con esta función que permite usar microfono o camara web
 navigator.getUserMedia({audio: true}, exito, error); //En caso de que si, habilitamos audio y se ejecutan las funciones, en caso de exito o error.
 } else {
 console.log('¡Tu navegador no es compatible!, ¿No lo vas a acutalizar?'); //Si no es compatible, enviamos este mensaje.
 }
 }
//Funcion para parar la grabación y escucharla
 function parar() {
 recorder.stop(); //Paramos la grabación
 recorder.exportWAV(function(s) { //Exportamos en formato WAV el audio
 audio.src = window.URL.createObjectURL(s); //Y convertimos el valor devuelto en URL para pasarlo a nuestro reproductor.
 });
 }