function setCookie(key, value) {
    var Days = 30;
    var exp = new Date();
    exp.setTime(exp.getTime() + Days * 24 * 60 * 60 * 1000);
    document.cookie = key + "=" + encodeURI(value) + ";expires=" + exp.toGMTString();
}

function getCookie(key) {
    var reg = new RegExp("(^| )" + key + "=([^;]*)(;|$)");
    var arr = reg.exec(document.cookie);

    if (arr) {
        return decodeURI(arr[2]);
    } else {
        return null;
    }
}

function delCookie(key) {
    var exp = new Date();
    var cval = getCookie(key);

    exp.setTime(exp.getTime() - 1);

    if (cval !== null)
        document.cookie = key + "=" + cval + ";expires=" + exp.toGMTString();
}
