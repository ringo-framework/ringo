/* Method to get the preferred user language. As there is no reliable
 * way to get this information accross all browsers the language is set
 * by the server in a meta variable in the html header */
function getLanguageFromBrowser() {
    return $("meta[name='client_language']").attr("content");
}
