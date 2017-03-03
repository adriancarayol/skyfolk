var max_height_comment = 60;
var flag_reply = false;

$(document).ready(function () {
    /* Show more - Show less */
    $('.container').find('.wrapper').each(function () {
        var comment = $(this).find('.wrp-comment');
        var show = $(this).find('.show-more a');

        if ($(comment).height() > max_height_comment) {
            $(show).show();
            $(comment).css('height', '2.6em');
        } else {
            //$(show).css('display', 'none');
        }
    });

    $('.wrapper').on('click', '.show-more a', function () {
        var $this = $(this);
        var $content = $this.parent().prev("div.comment").find(".wrp-comment");
        var linkText = $this.text().toUpperCase();

        if (linkText === "+ MOSTRAR MÁS") {
            linkText = "- Mostrar menos";
            $content.css('height', 'auto');
        } else {
            linkText = "+ Mostrar más";
            $content.css('height', '2.6em');
        }
        $this.text(linkText);
        return false;
    });

    /* Abrir respuesta a comentario */
    $('.container').on('click', '#options-comments .fa-reply', function () {
        var id_ = $(this).attr("id").slice(6);
        console.log(id_);
        if (flag_reply) {
            $("#" + id_).slideUp("fast");
            flag_reply = false
        } else {
            $("#" + id_).slideDown("fast");
            flag_reply = true
        }
    });
}); // END DOCUMENT