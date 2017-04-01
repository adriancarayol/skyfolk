$.getJSON('/emoji/all.json', function (data) {
    $('#message2, #message-reply').textcomplete([
        { // emoji strategy
            match: /\B:([\-+\w]*)$/,
            search: function (term, callback) {
                callback($.map(data, function (key, emoji) {
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
});