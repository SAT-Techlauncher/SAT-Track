$(document).ready(function () {
    $.get(
        '/getPriorityList',
        { 'user' : 0 },
        function (data) {

        }
    );

    var task = generateTask(0, 1, 'GPS 2020-03-22 xxx');

    $('#tasks').html(task);


});

function generateTask(index, priority, satellite) {
    var res =
        "<div class='task' data='" + index + "'>" +
        "    <div class='order_up'></div>" +
        "    <div class='order_down'></div>" +
        "    <p class='satellite_name'>" + priority + ". " + satellite + "</p>" +
        "    <div class='delete_task'></div>" +
        "</div>";
    return res
}
