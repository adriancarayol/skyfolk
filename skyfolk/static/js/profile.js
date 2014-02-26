<script> 
$(document).ready(function(){
  $("#flip").click(function(){
    $("#panel1").slideToggle("slow");
  });
});
</script>
<script> 
$(document).ready(function(){
  $("#Menu").mouseover(function(){
    $("#panel").slideToggle("slow");
	  });
});

$(document).ready(function(){
  $("#Menu").mouseover(function(){
    $("#panel").animate({
      left:'250px',
      opacity:'0.9',
      height:'300px',
      width:'300px'
    });
  });
});
</script> 
<script language="javascript">
function aparecerbola(){
	document.getElementById("widget").style.opacity = "0.9";
	document.getElementById("widget").style.webkitTransition = "opacity 1s linear";
}
function cambiopagina(){
	document.getElementById("widget").style.opacity = "0";
	document.getElementById("widget").style.webkitTransition = "opacity 0.9s linear";
	setTimeout('location.href="columnas.php"', 500);
}
function cambiopagina(){
	document.getElementById("widget").style.opacity = "0";
	document.getElementById("widget").style.webkitTransition = "opacity 0.9s linear";
	setTimeout('location.href="columnas.php"', 500);
}




</script>

