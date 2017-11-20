some = Function.prototype.call.bind([].some);

/* Method to get the preferred user language. As there is no reliable
 * way to get this information accross all browsers the language is set
 * by the server in a meta variable in the html header */
function getLanguageFromBrowser() {
    return $("meta[name='client_language']").attr("content");
}

function getApplicationPath() {
    return $("meta[name='application_path']").attr("content");
}

function getDTLanguage(language) {
    /* Helper method to translate the language setting of the browser into
    the equivalent option needed for the data tables plugin to load the
    correct language setting. */
    if (language.indexOf("de") >= 0) {
        return "german"
    } else {
        return "default";
    }
}
