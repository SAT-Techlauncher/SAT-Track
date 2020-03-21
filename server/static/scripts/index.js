
$(document).ready(function () {
    $('#search_button_a').on('click', function (event) {
        event.preventDefault();
        var satellite_id = $('#satellite_input').val(); //get satellite id
        console.log(satellite_id);

        $.post(
            '/search_satellite',
            {
                'id': satellite_id
            },
            function(data, status){
                if (status === "success") {
                    res = JSON.stringify(data);
                    alert(res);
                }
            });

        return false;
    });
});