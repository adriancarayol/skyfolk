$(document).ready(function () {
    $('.chips-placeholder').material_chip({
        placeholder: 'Introduce un tema',
        secondaryPlaceholder: '+Música, +Cine...'
    });
    $('.progress').fadeOut();

    $('.chips').find('.input').css('background-color', 'white');

    var form = $('#submit-themes');

    form.submit(function () {
        var tags = $('.chips').material_chip('data');
        var text_tag = [];
        for(var i = 0; i < tags.length; i++) {
            text_tag.push(tags[i].tag);
        }
        var myCheckboxes = [];
        $("input:checked").each(function() {
           myCheckboxes.push($(this).val());
        });
        $.ajax({
            type: form.attr('method'),
            url: "/topics/",
            data: {
                'csrfmiddlewaretoken': csrftoken,
                'tags[]': text_tag,
                'choices[]': myCheckboxes
            },
            cache: false,
            dataType: "json",
            success: function (response) {
                if (response == true) {
                    console.log('Submit themes OK')
                } else {
                    console.log('Failed on submit themes');
                }
            },
            error: function (rs, e) {
                alert('Error');
            }
        });
        return false;
    });
});

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
    beforeSend: function (xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});