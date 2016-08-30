$(document).ready(function () {
        $('#upload_new_photo').on('submit', function(event) {
        event.preventDefault();
        var data = $('#upload_new_photo').serialize();
        AJAX_upload_photo(data);
    });
});

function AJAX_upload_photo(data) {
    $.ajax({
        url: '/upload_new_photo/',
        type: 'POST',
        dataType: 'json',
        data: data,
        success: function(data) {
          var response = data.response;
          console.log('RESPONSE AQUI: ' + response + " type: " + type);
          if (response == true) {
            swal({
                title: "Success!",
                text: "Has subido una nueva foto!",
                type: "success",
                timer: 900,
                animation: "slide-from-top",
                showConfirmButton: false
            });
          } else {
            swal({
              title: "",
              text: "Failed to upload",
              type: "error"
            });
          }
        },
        error: function(rs, e) {
          alert('ERROR: ' + rs.responseText + " " + e)
        }
  }).done(function() {
      //addNewPublication(type, pks[0], pks[1], pks[2]);
  })
}