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