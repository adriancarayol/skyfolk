function setfirstLogin() {
  AJAX_set_login();
}

function AJAX_set_login() {
$.ajax({
    type: "POST",
    url: "/setfirstLogin/",
    data: {
      'csrfmiddlewaretoken': csrftoken
    },
    dataType: "json",
    success: function(response) {
      if (response == true) {
        alert("HEY");
      } else {
        alert("Hola");
      }
    },
    error: function(rs, e) {
      alert(rs.responseText);
    }
  });
}
