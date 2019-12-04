// 获取token
function get_tokens (res) {
    for (var data = res.data, arr = data.v.split(","), fnStr = "", i = 0; i < arr.length; i++)
        fnStr += String.fromCharCode(arr[i]);
    return fnStr;
}