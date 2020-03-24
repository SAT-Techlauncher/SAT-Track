
var isEmailOK = false,
    isPasswordOK = false,
    isRepasswordOK = false;

var isEmailExisted = false;

var emailPattern = /^[A-Za-z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$/,
    passwordPattern = /^[0-9]{1,18}$/; // /^(?![0-9]+$)(?![a-z]+$)(?![A-Z]+$)(?!([^(0-9a-zA-Z)])+$)^.{8,}$/;

var emailTip = "Mailbox format is not correct!",
    passwordTip = "8+ chars, 1+ num, upper, lower & spec",
    repasswordTip = "Please confirm password!",
    nullTip = "Please enter your email",
    consistencyTip = "Entered passwords must be consistent!",
    emailExistTip = "The email has existed!";

function changeSucceedStyle(nameID, spanID) { //SUCCESSFUL INPUT
    spanID.text("*");
    spanID.css('font-size', 'larger');
    spanID.css('color', 'blue');
    nameID.css('border-color', 'blue');
}

function changeFailedStyle(nameID, spanID) { //FAILED INPUT
    spanID.text("*");
    spanID.css('font-size', 'larger');
    spanID.css('color', 'red');
    nameID.css('border-color', 'red');
}

function changeFailingStyle(nameID, spanID) { //FAILED INPUT AND CURSOR IN THAT SAPN
    spanID.css('font-size', 'small');
    spanID.css('color', 'red');
    nameID.css('border-color', 'red');
}

function registerEmail() {
    var email = $("#register_email_input"); //get email
    var emailSpan = $("#register_email_span"); //get email span

    email.focus(function () { //获得焦点时根据匹配成功与否修改span中的样式和内容
        if (emailPattern.test(email.val())) { //匹配成功的话
            changeSucceedStyle(email, emailSpan); //修改为匹配成功的样式
        } else if (email.val() !== "") {
            emailSpan.text(emailTip);
            changeFailingStyle(email, emailSpan);
        } else {
            emailSpan.text(nullTip); //修改提示语句
            changeFailingStyle(email, emailSpan);
        }
    });

    email.keyup(function () { //输入内容是判断根据输入的值修改span中的样式和内容,使用up不是down，因为down读取时候有出入
        if (emailPattern.test(email.val())) { //匹配成功的话
            changeSucceedStyle(email, emailSpan); //修改为匹配成功的样式
        } else { //匹配失败
            emailSpan.text(emailTip); //修改提示语句
            changeFailingStyle(email, emailSpan);
        }
    });

    email.blur(function () { //失去焦点时根据匹配成功与否修改span中的样式和内容
        if (emailPattern.test(email.val())) { //匹配成功的话
            changeSucceedStyle(email, emailSpan); //修改为成功的样式
            isEmailOK = true;
        } else { //匹配失败
            changeFailedStyle(email, emailSpan); //修改为失败的样式
            isEmailOK = false;
        }

        $.ajax({
            url: '/validate',
            type: "post",
            headers: {'X-csrftoken': $('#register_csrf_input').val()},
            data: {'email': email.val()},
            success: function (data) {
                console.log(data.code);
                if (data.code !== 0) {
                    isEmailExisted = true;
                    emailSpan.text(emailExistTip);
                    changeFailingStyle(email, emailSpan);
                } else {
                    isEmailExisted = false;
                }
            }
        });
    });
}

function registerPassword() {
    var password = $("#register_password_input"); //得到密码的对象
    var passwordSpan = $("#register_password_span");
    var repassword = $("#register_repassword_input");
    var repasswordSpan = $("#register_repassword_span");

    password.focus(function () { //获得焦点时根据匹配成功与否修改span中的样式和内容
        if (passwordPattern.test(password.val())) {
            changeSucceedStyle(password, passwordSpan);
        } else { //如果获得焦点时输入不正确，重新调整样式
            passwordSpan.text(passwordTip); //修改提示语句
            changeFailingStyle(password, passwordSpan);
        }
    });

    password.keyup(function () { //输入内容是判断根据输入的值修改span中的样式和内容,使用up不是down，因为down读取时候有出入
        if (passwordPattern.test(password.val())) {
            changeSucceedStyle(password, passwordSpan);
            if (password.val() === repassword.val()) {
                changeSucceedStyle(repassword, repasswordSpan);
                isRepasswordOK = true;
            }
        } else { //如果获得焦点时输入不正确，重新调整样式
            passwordSpan.text(passwordTip); //修改提示语句
            changeFailingStyle(password, passwordSpan);
        }
    });

    password.blur(function () { //失去焦点时根据匹配成功与否修改span中的样式和内容
        if (passwordPattern.test(password.val())) {
            changeSucceedStyle(password, passwordSpan);
            isPasswordOK = true;
            repassword.focus();
        } else { //如果获得焦点时输入不正确，重新调整样式
            changeFailedStyle(password, passwordSpan);
            isPasswordOK = false;
        }
    });
}

function registerRepassword() {
    var password = $("#register_password_input");
    var repassword = $("#register_repassword_input"); //得到确认密码的样式
    var repasswordSpan = $("#register_repassword_span");

    repassword.focus(function () {
        if (isPasswordOK && password.val() === repassword.val()) {
            changeSucceedStyle(repassword, repasswordSpan);
        } else if (!isPasswordOK) { //如果获得焦点时输入不正确，重新调整样式
            repasswordSpan.text(repasswordTip); //修改提示语句
            changeFailingStyle(repassword, repasswordSpan);
        } else {
            repasswordSpan.text(consistencyTip); //修改提示语句
            changeFailingStyle(repassword, repasswordSpan);
        }
    });

    repassword.keyup(function () {
        if (isPasswordOK && password.val() === repassword.val()) {
            changeSucceedStyle(repassword, repasswordSpan);
            repassword.blur();
        } else if (!isPasswordOK) { //如果获得焦点时输入不正确，重新调整样式
            repasswordSpan.text(repasswordTip); //修改提示语句
            changeFailingStyle(repassword, repasswordSpan);
        } else {
            repasswordSpan.text(consistencyTip); //修改提示语句
            changeFailingStyle(repassword, repasswordSpan);
        }
    });

    repassword.blur(function () {
        if (isPasswordOK && password.val() === repassword.val()) {
            changeSucceedStyle(repassword, repasswordSpan);
            isRepasswordOK = true;
        } else {
            changeFailedStyle(repassword, repasswordSpan);
            isRepasswordOK = false;
        }
    });
}

function registerSubmit() { //对提交按钮进行设置
    var submit = $("#register_submit_input");
    var email = $("#register_email_input");
    var password = $("#register_password_input");
    var repassword = $("#register_repassword_input");
    submit.click(function () {
        if (isEmailOK && isPasswordOK && isRepasswordOK && !isEmailExisted) {
            setCookie('email', email.val());
            setCookie('password', password.val());
            return true;
        } else { //否则对填写错误的那项进行聚焦，来提示错误
            if (!isRepasswordOK)
                repassword.focus();
            if (!isPasswordOK)
                password.focus();
            if (!isEmailOK || isEmailExisted)
                email.focus();
            alert("Please check information!");
            return false;
        }
    });
}

$(document).ready(function() {
    registerEmail();
    registerPassword();
    registerRepassword();
    registerSubmit();
});