var username = '';
var priority = [];

$(document).ready(function () {
    // get username and priority list from server
    var tasks = $('#tasks');

    $.get(
        '/getUserInfo',
        function(data) {
            username = data.username;
            priority = data.priority;

            $('#user_name').text(username);

            var tasksHtml = generateTasks(priority);
            tasks.html(tasksHtml);

            initTaskColor(tasks);
        }
    );

    // user click up arrow button of a task
    tasks.on('click', '.task .order_up', function (event) {
        event.stopPropagation();

        var id = $(this).parent().attr('id');
        var index = $(this).parent().attr('data-index');
        var satId = $(this).parent().attr('data-satId');

        console.log("order up: " + index + ", " + satId + ", " + id + ", " + $('#' + id).text());

        $.get(
            '/orderUpTask',
            { 'id': satId },
            function (data) {
                if (data.code === 0) {
                    priority = data.priority;
                    var tasksHtml = generateTasks(priority);
                    tasks.html(tasksHtml);
                } else {
                    priority = data.priority;
                    tasks.html('');
                }
                initTaskColor(tasks);
            }
        );
    });

    // user click down arrow button of a task
    tasks.on('click', '.task .order_down', function (event) {
        event.stopPropagation();

        var id = $(this).parent().attr('id');
        var index = $(this).parent().attr('data-index');
        var satId = $(this).parent().attr('data-satId');

        console.log("order down: " + index + ", " + satId + ", " + id + ", " + $('#' + id).text());

        $.get(
            '/orderDownTask',
            { 'id': satId },
            function (data) {
                if (data.code === 0) {
                    priority = data.priority;
                    var tasksHtml = generateTasks(priority);
                    tasks.html(tasksHtml);
                } else {
                    priority = data.priority;
                    tasks.html('');
                }
                initTaskColor(tasks);
            }
        );
    });

    // user click delete button of a task
    tasks.on('click', '.task .delete_task', function (event) {
        event.stopPropagation();

        var id = $(this).parent().attr('id');
        var index = $(this).parent().attr('data-index');
        var satId = $(this).parent().attr('data-satId');

        console.log("delete: " + index + ", " + satId + ", " + id + ", " + $('#' + id).text());

        $.get(
            '/deleteTask',
            { 'id': satId },
            function (data) {
                if (data.code === 0) {
                    priority = data.priority;
                    var tasksHtml = generateTasks(priority);
                    tasks.html(tasksHtml);
                } else {
                    priority = data.priority;
                    tasks.html('');
                }
                initTaskColor(tasks);
            }
        );

    });

    // user click a task to activate it
    tasks.on('click', '.task', function (event) {
        var id = $(this).attr('id');
        var index = $(this).attr('data-index');
        var satId = $(this).attr('data-satId');

        console.log("activate: " + index + ", " + satId + ", " + id + ", " + $('#' + id).text());

        $.get(
            '/activateTask',
            { 'id': satId },
            function (data) {
                if (data.code === 0) {
                    var task = $('#' + id);

                    console.log(data.active);

                    if (data.active) {
                        $(task).removeClass('lighter');
                        $(task).addClass('darker');

                        setTimeout(function () {
                            $(task).css('background-color', '#fcff9b');
                        }, 500);
                    } else {
                        $(task).removeClass('darker');
                        $(task).addClass('lighter');

                        setTimeout(function () {
                            $(task).css('background-color', '#ffffff');
                        }, 500);
                    }

                    $(task).attr('data-active', data.active);
                }
            }
        );
    });

    var selectingSatellites = $('#selecting_satellites');

    // user type and search new satellite
    $('#submit_button').on('click', function (event) {
        event.preventDefault();

        var input = $('#satellite_input');
        var userInput = input.val();

        $.get(
            '/searchSatellite',
            { 'input': userInput },
            function (data) {
                if (data.code === 0) {
                    var satsHtml = generateSelectingSats(data.lst);
                    selectingSatellites.html(satsHtml);
                } else {
                    selectingSatellites.html('');
                }
            }
        );

        input.val('');
    });

    // user select a satellite into priority tasks list
    selectingSatellites.on('click', '.selecting_satellite', function (event) {
        var id = $(this).attr('id');
        var index = $(this).attr('data-index');
        var satId = $(this).attr('data-satId');

        console.log("select: " + index + ", " + satId + ", " + id + ", " + $('#' + id).text());

        $.get(
            '/selectSatellite',
            { 'id': satId },
            function (data) {
                if (data.code === 0) {
                    priority = data.priority;
                    var tasksHtml = generateTasks(priority);
                    tasks.html(tasksHtml);
                    selectingSatellites.html('');
                } else {
                    priority = data.priority;
                    tasks.html('');
                }
                initTaskColor(tasks);
            }
        );
    });

    enter('#submit_button');

});

function generateTasks(priority) {
    var html = '';
    for (var i = 0; i < priority.length; i++) {
        var noradId = priority[i].id;
        var satellite = priority[i].name;
        var latitude = 46.12;
        var longitude = 45.09;
        var active = priority[i].active;
        var executing = priority[i].executing;
        html +=
            "<div class='task' id='task_" + i + "' data-index='" + i + "' data-satId='" + noradId +
            "' data-active='" + active + "' data-executing='" + executing + "' >" +
            "<div class='order_up'></div>" +
            "<div class='order_down'></div>" +
            "<p class='satellite_name'>" + satellite + "</p>" +
            "<p class='norad_id'>norad id: " + noradId + "</p>" +
            "<p class='position'>" + latitude + "° &nbsp" + longitude + "°</p>" +
            "<div class='delete_task'></div>" +
            "</div>";
    }
    return html;
}

function initTaskColor(tasks) {
    var lst = tasks.children('.task');
    for (var i = 0; i < lst.length; i++) {
        var task = $(lst[i]);
        if (task.attr('data-active') === 'true')
            $(task).css('background-color', '#fcff9b');
        else
            $(task).css('background-color', '#ffffff');
    }
}

function enter(input) {
    $(input).keydown(function (e) {
        if (e.which === 13) {
            $(input).click();
        }
    });
}

function generateSelectingSats(lst) {
    var html = '';
    for (var i = 0; i < lst.length; i++) {
        var noradId = lst[i].norad_id;
        var name = lst[i].name;
        var intlCode = lst[i].intl_code;
        var launchDate = lst[i].launch_date;
        html +=
            "<div class='selecting_satellite' id='selecting_satellite_" + i + "' data-index='" + i +
            "' data-satId='" + noradId + "'>" +
            "<p class='selecting_name'>" + name + "</p>" +
            "<p class='selecting_norad_id'>" + noradId + "</p>" +
            "<p class='selecting_intl_code'>" + intlCode + "</p>" +
            "<p class='selecting_launch_date'>" + launchDate + "</p>" +
            "</div>"
        ;
    }
    return html;
}