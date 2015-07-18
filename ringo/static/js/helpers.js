/* Method to get the preferred user language. As there is no reliable
 * way to get this information accross all browsers the ask the server
 * for the language with gets this from the accepted header field */
function getLanguageFromBrowser() {
    $.ajax({
      url: "/rest/client/language",
    })
    .success(function( data ) {
        return data.data;
    });
}
