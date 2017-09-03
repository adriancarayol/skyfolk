var retrievedEmojis = localStorage.getItem('emojis');
var emojis;
if (retrievedEmojis === null) {
    $.getJSON('/emoji/all.json', function (data) {
        emojis = data;
        localStorage.setItem('emojis', JSON.stringify(data));
    });
}

var emojis = JSON.parse(retrievedEmojis);

$('#message2, .message-reply, #message3').textcomplete([
        { // emoji strategy
            match: /\B:([\-+\w]*)$/,
            search: function (term, callback) {
                callback($.map(emojis, function (key, emoji) {
                    return emoji.indexOf(term) === 0 ? emoji : null;
                }));
            },
            template: function (value) {
                return '<img src="/static/emoji/img/' + value + '.png"></img>' + value;
            },
            replace: function (value) {
                return ':' + value + ': ';
            },
            index: 1
        }
], {})