$(document).ready(function () {

   $('select').material_select();

   $('#btn-upload-photo').on('click', function () {
      $('#upload_photo').toggle();
   });

   $('#del-photo').click(AJAX_delete_photo);
}); // FIN DOCUMENT READY

/* DELETE OR EDIT PHOTO */
function AJAX_delete_photo() {
   var _id = $('.photo-body').attr('data-id');
   $.ajax({
      url: '/photo/sss/',
      type: 'DELETE',
      data: {
         'id': _id,
         'csrfmiddlewaretoken': csrftoken
      },
      dataType: 'json',
      success: function(json) {
         console.log(json);
      }, error: function(rs, e) {
         swal(rs.responseText + " " + e);
      }
   });
}