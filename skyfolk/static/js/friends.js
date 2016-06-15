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

function addProfileCard(username){
    $(".container").append('<a>Amigo: ' + username + '</a>');
}

/*PETICION AJAX PARA CARGAR + FOLLOWRS */
function AJAX_loadFollowers(){
    $.ajax({
        type: "POST",
        url: "/load_followers/",
        data: {'slug': 2, 'csrfmiddlewaretoken': csrftoken},
        dataType: "json",
        success: function(response) {
                          
            // load friends
            console.log("Loading followers");
            for (i=0;i<response.length;i++){
                console.log(response[i].user__username);
                addProfileCard(response[i].user__username);
            }
        },
        error: function(rs, e) {
            console.log(rs.responseText);
            console.log(e);
            response = JSON.parse(response);
            for (i=0;i<response.length;x++){
                addProfileCard(response[i].user__username);
            }
        }});
}

function AJAX_loadFollows(){
    $.ajax({
        type: "POST",
        url: "/load_follows/",
        data: {'slug': 2, 'csrfmiddlewaretoken': csrftoken},
        dataType: "json",
        success: function(response) {

            // load friends
            console.log("Loading follows");
            for (i=0;i<response.length;i++){
                console.log(response[i].user__username);
                addProfileCard(response[i].user__username);
            }
        },
        error: function(rs, e) {
            console.log(rs.responseText);
            console.log(e);
            response = JSON.parse(response);
            for (i=0;i<response.length;x++){
                addProfileCard(response[i].user__username);
            }
        }});
}