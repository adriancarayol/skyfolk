$(document).ready(function () {
    var $thread = $('#publication-thread');

   /* Borrar publicacion */
    $thread.on('click', '.trash-comment', function () {
        var publication_wrapper = $(this).closest('.infinite-item');
        var id = $(publication_wrapper).attr('id').split('-')[1];
        var board_group = $(publication_wrapper).data('id');
        console.log(id);
        console.log(board_group);
        swal({
            title: "¿Estás seguro?",
            text: "¡No podrás recuperar esta publicación!",
            type: "warning",
            animation: "slide-from-top",
            showConfirmButton: true,
            showCancelButton: true,
            confirmButtonColor: "#DD6B55",
            confirmButtonText: "Sí",
            cancelButtonText: "¡No!",
            closeOnConfirm: true
        }, function (isConfirm) {
            if (isConfirm) {
                AJAX_delete_group_publication(id, board_group);
            }
        });
    });

    /* Responder comentario */
    /* Abrir respuesta a comentario */
    $thread.on('click', '.reply-comment', function () {
        var id_ = $(this).attr("id").slice(6);
        $("#" + id_).slideToggle("fast");
    });

    /* Submit reply publication */
    $thread.on('click', '.group_reply', function (event) {
        event.preventDefault();
        var form = $(this).closest('form');
        var parent_pk = $(this).attr('id').split('-')[1];
        AJAX_submit_group_publication(form, 'reply', parent_pk);
    });

    /* ADD LIKE */
    $thread.on('click', '.like-comment', function () {
        var pub_box = $(this).closest('.row-pub');
        AJAX_add_like_group_publication(pub_box, $(this), "publication");
    });
    /* ADD HATE */
    $thread.on('click', '.hate-comment', function () {
        var pub_box = $(this).closest('.row-pub');
        AJAX_add_hate_group_publication(pub_box, $(this), "publication");
    });
    /* EDIT COMMENT */

    $thread.on('click', '.edit-comment', function () {
        Materialize.updateTextFields();
        var id = $(this).attr('data-id');
        $("#author-controls-" + id).slideToggle("fast");
    });

    $thread.on('click', '.edit-comment-btn', function (event) {
        event.preventDefault();
        var edit = $(this).closest('form').serialize();
        AJAX_edit_group_publication(edit);
    });

    $thread.on('click', '.wrapper .zoom-pub', function () {
        window.location.href = $(this).data('url');
    });
});