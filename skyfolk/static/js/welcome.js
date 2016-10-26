$(document).ready(function() {
  $('.chips-placeholder').material_chip({
    placeholder: 'Introduce un tema',
    secondaryPlaceholder: '+Música, +Cine...',
  });
});
window.onload = function() {
    $('.progress').fadeOut();
};

// using jQuery
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
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

/*
function AJAX_setLogin(username) {
  $.ajax({
    type: "POST",
    url: "/setfirstLogin/",
    data: {
      'csrfmiddlewaretoken': csrftoken,
      'username': username
    },
    dataType: "json",
    success: function(response) {
        if (response==true) {
        
        } else {
        
        }
    },
    error: function(rs, e) {
      alert(rs.responseText);
    }
  });
}
*/