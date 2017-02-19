$(function () {
    $("#li-tab-amigos").click(function () {
        $('#tab-amigos').css({
            "overflow": "auto"
        });
    });

    $("#li-tab-comentarios").click(function () {
        $('#tab-comentarios').css({
            "overflow": "auto"
        });

    });

    $("#li-tab-timeline").click(function () {
        $('#tab-timeline').css({
            "overflow": "auto"
        });
    });
}); // end document ready

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
            var _response = response.response;
            console.log(_response);
            if (_response === "user_add") {
                $('#follow-group').attr({
                    "id": "unfollow-group",
                    "class": "fa fa-remove group-follow",
                    "style": "color: #29b203;"
                });
            } else if (_response === "own_group") {
                swal({
                    title: "¡Ups!",
                    text: "¡No puedes seguir a tu propio grupo!",
                    customClass: 'default-div'
                });
            } else {
                swal({
                    title: "¡Ups!",
                    text: "Hay un error con tu petición, intentalo de nuevo mas tarde.",
                    customClass: 'default-div'
                });
            }
        },
        error: function (rs, e) {

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
                    "class": "fa fa-plus group-follow",
                    "style": "color: #555;"
                });
            } else if (response == false) {
                swal({
                    title: "¡Ups!",
                    text: "Hay un error con tu petición, intentalo de nuevo mas tarde.",
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
            var _response = response.response;
            var _numLikes = $("#likes");
            if (_response === "like") {
                $("#like-group").css('color', '#ec407a');
                $(_numLikes).find("strong").html(parseInt($(_numLikes).find("strong").html()) + 1);
            } else if (_response === "no_like") {
                $("#like-group").css('color', '#46494c');
                if ($(_numLikes).find("strong").html() > 0) {
                    $(_numLikes).find("strong").html(parseInt($(_numLikes).find("strong").html()) - 1);
                }
            } else if (_response === "own_group") {
                swal({
                    title: "¡Ups!",
                    text: "¡No puedes dar like a tu propio grupo!",
                    customClass: 'default-div'
                });
            } else {
                swal({
                    title: "¡Ups!",
                    text: "Hay un error con tu petición, intentalo de nuevo mas tarde.",
                    customClass: 'default-div'
                });
            }
        }, error: function (rs, e) {
            // alert(rs.responseText);
        }
    });
}
