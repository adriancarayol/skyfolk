$(document).ready(function () {
    $('#submit_poll_response').on('submit', function () {
        return false;
    });
    $('.vote').click(function (event) {
       var form = $(this).closest('form');
       $.ajax({
            data: form.serialize() + "&submit=" + $(this).attr("name"),
            type: form.attr('method'),
            url: form.attr('action'),
            success: function (data) {
                if (data.response[0] === true) {
                    addData(myChart, data.value_of_no[0], data.value_of_yes);
                }
            }
        });
    });
});

function addData(chart, value_of_no, value_of_yes) {
    chart.data.datasets[0].data[0] = value_of_no;
    chart.data.datasets[0].data[1] = value_of_yes;
    chart.update();
}