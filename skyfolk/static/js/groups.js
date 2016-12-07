function AJAX_follow_group(_id) {
    $.ajax({
        url: '/follow_group/',
        data: {
            'id': _id,
            'csrfmiddlewaretoken': csrftoken
        },
        type: 'POST',
        success: function (response) {
            alert(response)
        },
        error: function (rs, e) {
            alert('ERROR: ' + rs.responseText + e);
        }
    });
}

function AJAX_unfollow_group(_id) {
    $.ajax({
        type: 'POST',
        url: '/unfollow_group/',
        data: {
            'id': _id,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (response) {
            if (response == "user_unfollow") {
                alert('OK');
            } else if (response == false) {
                swal({
                    title: "¡Ups!",
                    text: "Ha surgido un error, inténtalo de nuevo más tarde :-(",
                    customClass: 'default-div'
                });
            }
        }, error: function (rs, e) {
            // swal(rs.responseText + " " + e);
        }
    });
}