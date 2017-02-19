$(document).ready(function () {
    /* Show more - Show less */
    $('#tab-messages').find('.wrapper').each(function () {
        var showLimitChar = 90;
        var comment = $(this).find('.wrp-comment');
        var text = comment.text();
        var show = $(this).find('.show-more a');
        text = text.replace(/\s\s+/g, ' ');

        if (text.length < showLimitChar) {
            $(show).css('display', 'none');
        }
    });

    $("#tab-messages").on('click', '.show-more a', function () {
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

    /* Expandir comentario */

    $('.fa-expand').on('click', function () {
        var caja_pub = $(this).closest('.wrapper');
        expandComment(caja_pub);
    });

    function expandComment(caja_pub) {
        var id_pub = $(caja_pub).attr('id').split('-')[1];  // obtengo id
        var commentToExpand = document.getElementById('expand-' + id_pub);
        $(commentToExpand).fadeToggle("fast");
    }

    /* Cerrar comentario expandido */

    $('.cerrar_ampliado').on('click', function () {
        var expand = $(this).closest('.ampliado');
        closeExpand(expand);
    });

    function closeExpand(expand) {
        var c = $(expand).attr('id').split('-')[1];
        var toClose = document.getElementById('expand-' + c);
        $(toClose).hide();
    }
});