$(document).ready(function () {
    var _group_profile = $('#group-profile');
    // FOLLOW GROUP
    $(_group_profile).on('click', '#follow-group', function () {
        var id = $(_group_profile).attr('data-id');
        AJAX_follow_group(id);
    });
    // UNFOLLOW GROUP
    $(_group_profile).on('click', '#unfollow-group', function () {
        var id = $(_group_profile).attr('data-id');
        AJAX_unfollow_group(id);
    });

    // LIKE GROUP
    $(_group_profile).on('click', '#like-group', function () {
        var id = $(_group_profile).attr('data-id');
        AJAX_like_group(id);
    });
});

function AJAX_follow_group(_id) {
    $.ajax({
        type: 'POST',
        url: '/follow_group/',
        data: {
            'id': _id,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (response) {
            if (response.localeCompare("user_add") == 0) {
                $('#follow-group').attr({
                    "id": "unfollow-group",
                    "class": "fa fa-remove group-follow"
                });
            } else {

            }
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
                $('#unfollow-group').attr({
                    "id": "follow-group",
                    "class": "fa fa-plus group-follow"
                });
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

function AJAX_like_group(_id) {
    $.ajax({
        type: 'POST',
        url: '/like_group/',
        data: {
            'id': _id,
            'csrfmiddlewaretoken': csrftoken
        },
        dataType: 'json',
        success: function (response) {
            var _numLikes = $("#likes");
            if (response == "like") {
                $("#like-group").css('color', '#ec407a');
                $(_numLikes).find("strong").html(parseInt($(_numLikes).find("strong").html()) + 1);
            } else if (response == "no_like") {
                $("#like-group").css('color', '#46494c');
                if ($(_numLikes).find("strong").html() > 0) {
                    $(_numLikes).find("strong").html(parseInt($(_numLikes).find("strong").html()) - 1);
                }
            } else {
               console.log("...");
            }
        }, error: function (rs, e) {
            // alert(rs.responseText);
        }
    });
}