var notify_badge_id;
var notify_menu_id;
var notify_api_url;
var notify_fetch_count;
var notify_unread_url;
var notify_mark_all_unread_url;
var notify_refresh_period = 15000;
var consecutive_misfires = 0;
var registered_functions = [];

function fill_notification_badge(data) {
    var badge = document.getElementById(notify_badge_id);
    if (badge) {
        badge.innerHTML = data.unread_count;
    }
}

function fill_notification_list(data) {
    var menu = document.getElementById(notify_menu_id);
    if (menu) {
        menu.innerHTML = "";
        for (var i=0; i < data.unread_list.length; i++) {
            var item = data.unread_list[i];
            console.log(item);
            var message = '<a onclick="AJAX_mark_read(this)" class="fa fa-remove" id="mark-as-read-notification" data-notification="' + item.slug + '"/></a>';
            if (item.actor_avatar !== null && typeof item.actor_avatar !== 'undefined') {
                message = message + " <img class=\"circle\" src=\"" + item.actor_avatar + '"/>';
            }
            if(typeof item.actor !== 'undefined' && item.level !== 'new_follow'){
                message = message + "<a class=\"title\" href=\"/profile/" + item.actor + '" >' + item.actor + '</a>';
            }

            if(typeof item.verb !== 'undefined'){
                message = message + " <span class=\"title\"/>" + item.verb + '</span>';
            }

            if(typeof item.target !== 'undefined'){
                message = message + " " + item.target;
            }
            if(typeof item.description !== 'undefined' && item.description != null){
                message = message + " " + item.description;
            }
            if(typeof item.timestamp !== 'undefined'){
                message = message + "<p><i>" + item.timestamp + '</i></p>';
            }
            if (typeof item.level !== 'undefined' && item.level == 'friendrequest') {
                message = message + " <div class=\"notification-buttons\"><" +
'button data-notification="' + item.slug + '" onclick="AJAX_respondFriendRequest(\'' + item.actor_object_id + '\',\'' + "accept" + '\',\'' + item.id + '\'); AJAX_delete_notification(\'' + item.slug + '\',\'' + item.id + '\')" class="accept-response waves-effect waves-light btn white-text green"><i class="material-icons">done</i></button>\<' +
                    'button data-notification="' + item.slug + '" onclick="AJAX_respondFriendRequest(\'' + item.actor_object_id + '\',\'' + "rejected" + '\',\'' + item.id + '\'); AJAX_delete_notification(\'' + item.slug + '\',\'' + item.id + '\')" class="rejected-response waves-effect waves-light btn white-text red"> <i class="material-icons">cancel</i></button>\<' +
                    '/div>';
            }
            message += "<a href=\"#!\" class=\"secondary-content\"><i class=\"material-icons\">people<\/i><\/a>";
            menu.innerHTML = menu.innerHTML + '<li class=\"collection-item avatar\" data-id="' + item.id + '">'+ message + '</li>';
        }
    }
}

function register_notifier(func) {
    registered_functions.push(func);
}

function fetch_api_data() {
    if (registered_functions.length > 0) {
        //only fetch data if a function is setup
        var r = new XMLHttpRequest();
        r.open("GET", notify_api_url+'?max='+notify_fetch_count, true);
        r.onreadystatechange = function () {
            if (r.readyState != 4 || r.status != 200) {
                consecutive_misfires++;
            }
            else {
                consecutive_misfires = 0;
                for (var i=0; i < registered_functions.length; i++) {
                    var func = registered_functions[i];
                    func(JSON.parse(r.responseText));
                }
            }
        };
        r.send();
    }
    if (consecutive_misfires < 10) {
        setTimeout(fetch_api_data,notify_refresh_period);
    } else {
        var badge = document.getElementById(notify_badge_id);
        if (badge) {
            badge.innerHTML = "!";
            badge.title = "Connection lost!"
        }
    }
}

setTimeout(fetch_api_data,1000);
