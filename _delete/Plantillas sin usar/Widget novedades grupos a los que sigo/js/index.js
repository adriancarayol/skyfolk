$('ul.controls span').click(function() {
  if($(this).hasClass('.green')){
       $(this).removeClass('.green'); 
  }
  else {
       $(this).addClass('.green');
  }
});