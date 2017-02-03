$(document).ready(function () {

   $('select').material_select();

   $('#btn-upload-photo').on('click', function () {
      $('#upload_photo').toggle();
   });

   $('#del-photo').click(AJAX_delete_photo);


   $("#edit-photo").click(function () {
      $(this).text(function(i, text){
          return text === "Editar" ? "No editar" : "Editar";
      });

      $('#wrapper-edit-form').toggle();

       return false;
   });

    $('.tags-content').on('click', 'blockquote', function () {
        $(this).nextAll('input').click();
    });

    $('#crop-image').on('click', function () {
       $('#crop-image-preview').show();
    });
}); // FIN DOCUMENT READY

/* DELETE OR EDIT PHOTO */
function AJAX_delete_photo() {
   var _id = $('.photo-body').attr('data-id');
   $.ajax({
      url: '/delete/photo/',
      type: 'DELETE',
      data: {
         'id': _id,
         'csrfmiddlewaretoken': csrftoken
      },
      dataType: 'json',
      success: function(json) {
         swal({
                  title: "Photo was deleted.",
                  text: json.msg,
                  timer: 2500,
                  showConfirmButton: true
         }, function () {
            window.location.replace('/multimedia/'+json.author+'/');
         });
      }, error: function(rs, e) {
         swal(rs.responseText + " " + e);
      }
   });
}
