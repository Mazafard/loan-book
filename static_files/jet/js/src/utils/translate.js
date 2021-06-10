module.exports = function (str) {
    if (window.django == undefined) {
        return str;
    }
    return gettext(str);
};
