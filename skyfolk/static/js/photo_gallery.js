$(document).ready(function () {

   $('select').material_select();

   $('#btn-upload-photo').on('click', function () {
      $('#upload_photo').toggle();
   });
}); // FIN DOCUMENT READY