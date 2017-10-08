$(document).ready(function () {
    $('#btn-notifications').on('click', function (e) {
        e.preventDefault();
        var form = $(this).closest('form');
        $.ajax({
            url: form.attr('action'),
            type: 'POST',
            data: form.serialize(),
            success: function(data, textStatus, jqXHR) {
                  Materialize.toast('Configuracion guardada. ¡Todo listo!', 4000) // 4000 is the duration of the toast
            },
            error: function(data, textStatus, jqXHR) {
               swal({
                    title: "Tenemos un problema...",
                    customClass: 'default-div',
                    text: "Hubo un problema con su petición.",
                    timer: 4000,
                    showConfirmButton: true
                });
            }
        });
    });
});

function toProfile(url) {
    document.location.href = url;
}