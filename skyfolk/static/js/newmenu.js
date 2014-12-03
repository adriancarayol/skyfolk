var items = document.querySelectorAll('.circle a');

for(var i = 0, l = items.length; i < l; i++) {
  items[i].style.left = (20 - 30*Math.cos(-0.5 * Math.PI - 2*(1/l)*i*Math.PI)).toFixed(4) + "%";
  
  items[i].style.top = (35 + 35*Math.sin(-0.5 * Math.PI - 2*(1/l)*i*Math.PI)).toFixed(4) + "%";
}

document.querySelector('.profile').onclick = function(e) {
   e.preventDefault(); document.querySelector('.circle').classList.toggle('open');
}
