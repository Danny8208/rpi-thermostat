var default_cookie_values = {
    "background_color": "#222222",
    "idle_color": "#1e1e1e",
    "running_color": "#e24306",
    "temperature_scale": "fahrenheit"
}
function checkAndSetCookies() {
    for (let key in default_cookie_values) {
        if (Cookies.get(key) == undefined) {
            Cookies.set(key, default_cookie_values[key], { expires: new Date(3000, 0) })
        }
        if (key == "temperature_scale") $('input[name="temperature_scale"]').val([Cookies.get(key)])
        else $("#" + key).val(Cookies.get(key))
    }
}
function convertCF(c_temp) {
    return Number(c_temp) * 9 / 5 + 32
}
function convertFC(f_temp) {
    return (Number(f_temp) - 32) * 5 / 9
}
function roundToHalf(num) {
    return Math.round(Number(num) * 2) / 2;
}
