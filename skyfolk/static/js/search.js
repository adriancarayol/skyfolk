$(document).ready(function () {
    $('li.list-vertical:nth-child(6)').on('click', function (e) {
        if (e.target !== this) return;
        $(this).find('.dropdown-options').toggleClass('dropdown-options-open');
    });

    $(this).click(function(event) {
        if(!$(event.target).closest('.list-vertical').length) {
            if($('#dropdown-search').is(":visible")) {
                $('#dropdown-search').removeClass('dropdown-options-open');
            }
        }
    });

    $(this).on('keydown', function(e) {
        if (e.keyCode === 27) { // escape
            var messageWrapper = document.getElementById('dropdown-search');
            $(messageWrapper).removeClass('dropdown-options-open');
        }
    });
});