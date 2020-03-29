$(document).ready(function () {
    var email = getCookie('email');
    var password = getCookie('password');

    $('#login_email_input').val(email);
    $('#login_password_input').val(password);

    setCookie('email', '');
    setCookie('password', '');
});