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



/* Comprueba si la URL de la imagen de usuario existe */
function isEmpty(str) {
    return (!str || 0 === str.length);
}

function addProfileCard(username, firstname, lastname, backImage){
    var MEDIA_URL = '/media/';
    var STATIC_URL = '/static/';
    var userImage;
    if (isEmpty(backImage)) {
        userImage = STATIC_URL + '/img/nuevo.png';
    } else {
        userImage = MEDIA_URL + backImage;
    }
    $(".container .container-responsive").append('<div class="col-lg-3 col-md-10 col-sm-12">' +
        '<div class="personal-card">' +
            '<div class="col-lg-12">' +
                '<div class="header">' +
                    '<img class="back-profile-user" src="' + userImage +'">' +
                    '<i class="fa fa-user fa-2x like-him">' +
                    '</i>' +
                    '<div class="bg-user">' +
                     '</div>' +
                '</div>' +
            '</div>' +
        '<div class="col-lg-12">' +
            '<div class="name-friend">' +
            '<a href="/profile/' + username + '">' + username + '</a><br><br>' +
            '<p>'+ firstname + ' ' + lastname + '</p>' +
            '</div>' +
        '</div>' +
        '</div>' +
        '</div>');
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
            for (var i=0;i<response.length;i++){
                console.log(response[i].user__username +
                console.log(response[i].user__first_name +
                console.log(response[i].user__last_name)));
                addProfileCard(response[i].user__username,
                    response[i].user__first_name, response[i].user__last_name, response[i].user__profile__backImage);
            }
        },
        error: function(rs, e) {
            console.log(rs.responseText);
            console.log(e);
            var response = JSON.parse(response);
            for (var i=0;i<response.length;x++){
                addProfileCard(response[i].user__username,
                    response[i].user__firstname, response[i].user__lastname, response[i].user__profile__backImage);
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
            for (var i=0;i<response.length;i++){
                console.log(response[i].user__username +
                console.log(response[i].user__first_name +
                console.log(response[i].user__last_name)));
                addProfileCard(response[i].user__username,
                    response[i].user__first_name, response[i].user__last_name, response[i].user__profile__backImage);
            }
        },
        error: function(rs, e) {
            console.log(rs.responseText);
            console.log(e);
            var response = JSON.parse(response);
            for (var i=0;i<response.length;x++){
                addProfileCard(response[i].user__username,
                    response[i].user__firstname, response[i].user__lastname, response[i].user__profile__backImage);
            }
        }});
}