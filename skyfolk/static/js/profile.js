
$(document).ready(function(){
  $("#flip").click(function(){
    $("#panel1").slideToggle("slow");
  });
});

$(document).ready(function(){
  $("#Menu").click(function(){
    $("#panel").slideToggle("slow");
	  });
});

$(document).ready(function(){
  $("#Menu").click(function(){
    $("#panel").animate({
      left:'250px',
      opacity:'0.9',
      height:'300px',
      width:'300px'
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
  $("#flip").click(function(){
    $("#panel1").slideToggle("slow");
  });
});

$(document).ready(function(){
  $(".nameact").click(function(){
    $("#panel1").slideToggle("slow");
	  });
});

$(document).ready(function(){
  $(".nameact").click(function(){
    $("#panel1").animate({
      left:'250px',
      opacity:'0.9',
      height:'80px',
      width:'80px'
    });
  });
});





